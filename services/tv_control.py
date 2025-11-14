from config.settings import TV_IP 
from services.voice_service import speak
from androidtv import setup

ADB_PORT = 5555
ADB_KEY_FILE = r"C:\Users\legal\OneDrive\Desktop\adb-tools\platform-tools\adbkey"
tv = None  # Armazena a conexão com a TV


def conectar_tv():
    global tv
    if tv is None:
        try:
            speak(f"Tentando conectar com a TV no IP {TV_IP}")

            tv = setup(
                TV_IP,
                port=ADB_PORT,
                adbkey=ADB_KEY_FILE
            )

            if tv.available:
                speak("Conexão com a TV estabelecida com sucesso!")
                return True
            else:
                tv = None
                speak("A TV não está disponível ou a depuração ADB não está ativada.")
                return False

        except Exception as e:
            tv = None
            print(f"Erro de conexão com a TV: {e}")
            speak("Não foi possível conectar. Verifique o ADB na TV.")
            return False
    return True


def enviar_comando_tv(comando):
    if conectar_tv():
        try:
            tv.adb_shell(f"input keyevent {comando}")
            return True
        except Exception as e:
            print(f"Erro ao enviar comando ADB: {e}")
            speak("Falha ao enviar o comando.")
            return False
    return False



def ligar_desligar():
    if enviar_comando_tv(26):
        speak("Comando ligar/desligar enviado.")


def aumentar_volume():
    if enviar_comando_tv(24): 
        speak("Aumentando o volume.")
