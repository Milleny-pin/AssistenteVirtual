import os
import pyttsx3
import google.generativeai as genai
from dotenv import load_dotenv
import threading

# 1. Carregar variáveis de ambiente
load_dotenv()

# 2. Configurar APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
TV_IP = os.getenv("TV_IP")
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Inicializar motores e estados globais
engine = pyttsx3.init()

# Variáveis globais para o Reconhecimento Facial
camera_thread = None
camera_stop_event = threading.Event()
# Conjunto de nomes dos rostos que estão sendo vistos pela câmera
global_recognized_faces_in_view = set()