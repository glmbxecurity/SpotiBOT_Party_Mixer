# SpotiBOT_Party_Mixer
Este programa es un bot de Telegram que permite a un usuario autorizado combinar múltiples playlists de Spotify en una nueva playlist privada, muy útil para fiestas con amigos en la que todos quereis oir vuestra musica!  

## Funcionamiento principal

- **Autorización Telegram:** Solo un usuario autorizado (por su ID de Telegram) puede usar el bot.
- **Entrada del usuario:** El usuario envía por mensaje de Telegram dos o más URLs o IDs de playlists de Spotify.
- **Combinación:** El bot extrae todas las canciones de esas playlists y las une, eliminando duplicados.
- **Creación:** Crea una nueva playlist privada en la cuenta de Spotify del usuario con todas las canciones combinadas.
- **Respuesta:** Envía al usuario el enlace a la nueva playlist creada.

## Instalación

Para usar SpotiBOT, primero necesitas tener Python 3.x (Probado en Python 3.13.0)  
Luego debes instalar `spotipy` y `python-dotenv`

```bash
pip install spotipy python-dotenv python-telegram-bot nest_asyncio
``` 

### 1. Clonar el repositorio

Clona el repositorio de GitHub en tu máquina local:

`git clone https://github.com/glmbxecurity/SpotiBOT_Party_Mixer.git`

### 2. Configuración

Antes de ejecutar el programa, necesitas configurar las credenciales de la API de Spotify. Para ello, crea un archivo `config.txt` en el directorio raíz del proyecto con la siguiente estructura:


```bash
SPOTIPY_CLIENT_ID=tu_client_id
SPOTIPY_CLIENT_SECRET=tu_client_secret
SPOTIPY_REDIRECT_URI=tu_redirect_uri
TELEGRAM_TOKEN=tu_telegram_token_del_bot
```
Estos valores los puedes obtener creando una aplicación en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).

![image](https://raw.githubusercontent.com/glmbxecurity/SpotiBOT/refs/heads/main/screenshots/config.jpeg)  
El token del bot de telegram se obtiene de la siguiente manera:  

1.  Abre Telegram y busca el **BotFather**.  
2.  Envía el comando `/newbot` y sigue las instrucciones para crear tu bot.  
3.  Una vez creado, **BotFather** te dará un Token que deberás copiar.

Por último debes obtener tu AUTHORIZED_USER_ID que deberas introducir en SpotiBOT_Party_Mixer.py, y se obtiene:  
Enviandote un mensaje a ti mismo y luego usar un bot como **UserInfoBot** en Telegram para obtener tu ID.  

### 3. Lanzar el Bot

Para lanzar el bot (en segundo plano):

1.  Abre una terminal en el directorio donde se encuentra el archivo `SpotiBOT_Party_Mixer.py`.
2.  Ejecuta el siguiente comando:


`nohup python3 SpotiBOT_Party_Mixer.py &` 

### Iniciar bot automaticamente con el S.O (Alpine Linux)  
Suponiendo que el bot está en **/root/SpotiBOT_Party_Mixer/SpotiBOT_Party_Mixer.py**  


1. Crea un archivo en /etc/init.d/partymixer con este contenido:
```bash
#!/sbin/openrc-run

name="partymixer"
description="PartyMixer Spotify Telegram Bot"

command="/usr/bin/python3"
command_args="/root/SpotiBOT_Party_Mixer/SpotiBOT_Party_Mixer.py"
pidfile="/run/${RC_SVCNAME}.pid"
command_background=true
directory="/root/SpotiBOT_Party_Mixer"

depend() {
    need net
    after firewall
}

start_pre() {
    checkpath --directory --mode 0755 /run/${RC_SVCNAME}
}
```
2. Iniciar con el equipo:
```bash
chmod +x /etc/init.d/partymixer
rc-update add partymixer default
rc-service partymixer start
rc-service partymixer status
```


