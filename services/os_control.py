import pyautogui
import webbrowser
import datetime
from services.voice_service import speak 

# --- Funções de Automação Básica ---
def mover_e_clicar(x, y):
    pyautogui.moveTo(x, y, duration=0.5)
    pyautogui.click()

def digitar_texto(texto):
    pyautogui.write(texto)

def pressionar_tecla(tecla):
    pyautogui.press(tecla)

# --- Funções de Abertura de Programas/Busca ---
def abrir_bloco_notas():
    pyautogui.press('win')
    pyautogui.sleep(1)
    pyautogui.write('bloco de notas')
    pyautogui.sleep(0.5)
    pyautogui.press('enter')
    speak("Bloco de Notas aberto.")

def abrir_spotify():
    pyautogui.press('win')
    pyautogui.sleep(1)
    pyautogui.write('Spotify')
    pyautogui.sleep(0.5)
    pyautogui.press('enter')
    speak('Spotify aberto')

def abrir_discord():
    pyautogui.press('win')
    pyautogui.sleep(1)
    pyautogui.write('discord')
    pyautogui.sleep(0.5)
    pyautogui.press('enter')
    speak('Discord aberto.')

def whatsapp():
    pyautogui.press('win')
    pyautogui.sleep(1)
    pyautogui.write('whatsapp')
    pyautogui.sleep(0.5)
    pyautogui.press('enter')
    speak('Zap aberto.')

def get_current_time():
    """Retorna a hora atual."""
    strTime = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"Senhorita, são {strTime}")

def search_google(query):
    """Abre o Google com a pesquisa."""
    webbrowser.open(f"https://www.google.com/search?q={query}")

def open_youtube():
    """Abre a página inicial do YouTube."""
    webbrowser.open("https://www.youtube.com/")

def search_youtube(query):
    """Abre o YouTube com a pesquisa."""
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")