#!/usr/bin/env python3
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

AUTHORIZED_USER_ID = 942135888  # Cambia por tu ID

def load_config():
    config = {}
    with open("config.txt") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                config[k] = v
    return config

def authenticate_spotify():
    config = load_config()
    scope = "playlist-read-private playlist-modify-private"
    sp_oauth = SpotifyOAuth(
        client_id=config["SPOTIPY_CLIENT_ID"],
        client_secret=config["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=config["SPOTIPY_REDIRECT_URI"],
        scope=scope,
        cache_path="token_cache.json"
    )
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        print("No hay token cacheado. Autoriza manualmente.")
        auth_url = sp_oauth.get_authorize_url()
        print(f"Abre este enlace en el navegador y autoriza: {auth_url}")
        redirect_response = input("Pega la URL completa a la que fuiste redirigido: ")
        code = sp_oauth.parse_response_code(redirect_response)
        token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp

def is_authorized_user(update: Update):
    return update.message.from_user.id == AUTHORIZED_USER_ID

def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id)
    while results:
        tracks.extend(results['items'])
        results = sp.next(results) if results['next'] else None
    return tracks

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized_user(update):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    msg = (
        "🎉 ¡Bienvenido a *SpotiBOT Party Mixer*! 🎶\n\n"
        "Envía 2 o más *URLs o IDs* de playlists de Spotify en un solo mensaje, separados por espacio.\n\n"
        "El bot combinará las canciones (sin duplicados) y creará una nueva playlist privada en tu cuenta.\n\n"
        "✅ Ejemplo:\n"
        "`https://open.spotify.com/playlist/xxx https://open.spotify.com/playlist/yyy`\n\n"
        "¡Disfruta de tu mezcla musical! 🪩"
    )
    await update.message.reply_markdown(msg)

async def combine_playlists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized_user(update):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Envía 2 o más URLs o IDs de playlists separados por espacios.")
        return

    playlist_ids = []
    for part in text.split():
        if "playlist/" in part:
            pid = part.split("playlist/")[1].split("?")[0]
            playlist_ids.append(pid)
        else:
            playlist_ids.append(part)

    if len(playlist_ids) < 2:
        await update.message.reply_text("Por favor, envía al menos 2 playlists para combinar.")
        return

    try:
        sp = authenticate_spotify()
        user_id = sp.current_user()["id"]

        combined_tracks = {}
        for pid in playlist_ids:
            full_id = f"spotify:playlist:{pid}"
            tracks = get_playlist_tracks(sp, full_id)
            for t in tracks:
                track = t.get('track')
                if track and track.get('id'):
                    combined_tracks[track['id']] = track['uri']

        if not combined_tracks:
            await update.message.reply_text("No se encontraron canciones en las playlists.")
            return

        track_uris = list(combined_tracks.values())

        new_name = "Combinada " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        new_playlist = sp.user_playlist_create(user_id, new_name, public=False,
                                               description="Playlist combinada creada con SpotiBOT Party Mixer")

        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            sp.playlist_add_items(new_playlist['id'], batch)

        await update.message.reply_text(f"✅ Playlist creada: {new_playlist['external_urls']['spotify']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al combinar playlists: {str(e)}")

async def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    config = load_config()
    TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, combine_playlists))
    await application.run_polling()

# --- Llamada segura con nest_asyncio ---
if __name__ == "__main__":
    import nest_asyncio
    import sys
    nest_asyncio.apply()

    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "event loop is already running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise
