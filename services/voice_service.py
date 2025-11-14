import speech_recognition as sr
# Importar variáveis do settings para usar o engine e as funções de outros módulos
from config.settings import engine

from services.ai_service import ask_gemini # É importante importar se precisar da IA

def speak(audio):
    """Fala o texto fornecido através do pyttsx3."""

    print(f'Luna: {audio}')
    engine.say(audio)
    engine.runAndWait()

def listen_command(timeout_duration=5):
    """Ouve o microfone e retorna o comando em minúsculas."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Luna: Ouvindo...")
        r.pause_threshold = 1.2
        try:
            audio = r.listen(source, timeout=timeout_duration)
            print("Luna: Reconhecendo...")
            query = r.recognize_google(audio, language='pt-br')
            print(f"Você disse: {query}\n")
            return query.lower()

        except sr.WaitTimeoutError:
            print("Luna: Nenhum áudio detectado no tempo limite.")
            return "none_timeout"
        except sr.UnknownValueError:
            print('Luna: Desculpe, não entendi o que você disse, fale novamente.')
            return 'none'
        except sr.RequestError as e:
            print(f"Luna: Não foi possível solicitar resultados do serviço de fala Google; {e}")
            return "none"