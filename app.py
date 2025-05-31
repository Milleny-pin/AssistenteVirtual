import speech_recognition as sr
import pyttsx3
import datetime
import os 
import pyautogui
import google.generativeai as genai 
from dotenv import load_dotenv
import webbrowser
import face_recognition
import cv2
import numpy as np
from fuzzywuzzy import fuzz
import threading 

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

gemini_model = genai.GenerativeModel('gemini-1.5-flash')

engine = pyttsx3.init()
camera_thread = None 
camera_stop_event = threading.Event() 
global_recognized_faces_in_view = set() 
def reconhecimento_facial_em_tempo_real_thread(stop_event, cam_index=0, cam_known_faces_paths=None):
    global global_recognized_faces_in_view

    if cam_known_faces_paths is None:
        cam_known_faces_paths = ["milleny_conhecida.jpg"] 

    rostos_conhecidos_codificacoes = []
    nomes_dos_rostos_conhecidos = []
    if isinstance(cam_known_faces_paths, str):
        cam_known_faces_paths = [cam_known_faces_paths]

    for caminho_rosto in cam_known_faces_paths:
        try:
            imagem_conhecida = face_recognition.load_image_file(caminho_rosto)
            codificacoes = face_recognition.face_encodings(imagem_conhecida)
            if codificacoes:
                rostos_conhecidos_codificacoes.append(codificacoes[0])
                nomes_dos_rostos_conhecidos.append(caminho_rosto.split('/')[-1].split('\\')[-1].split('.')[0])
            else:
                print(f"Aviso: Não encontrei rosto na imagem conhecida: {caminho_rosto}")
        except FileNotFoundError:
            print(f"Erro: Imagem conhecida não encontrada: {caminho_rosto}")
            stop_event.set() 
            return

    print("Rostos conhecidos carregados e codificados para a câmera.")
    
    video_capture = cv2.VideoCapture(cam_index)
    if not video_capture.isOpened():
        print("Erro: Não foi possível acessar a câmera. Verifique se ela está conectada e não está sendo usada por outro programa.")
        stop_event.set() 
        return

    print("Câmera acessada com sucesso. (Pressione 'q' na janela da câmera ou diga 'fechar câmera' para sair.)")
    while not stop_event.is_set(): 
        ret, frame = video_capture.read()
        if not ret:
            print("Erro: Não consegui ler o quadro da câmera.")
            break
        
        pequeno_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_pequeno_frame = cv2.cvtColor(pequeno_frame, cv2.COLOR_BGR2RGB)

        localizacoes_rostos = face_recognition.face_locations(rgb_pequeno_frame)
        codificacoes_rostos = face_recognition.face_encodings(rgb_pequeno_frame, localizacoes_rostos)

        current_frame_recognized_names = set() 
        for (top, right, bottom, left), codificacao_face in zip(localizacoes_rostos, codificacoes_rostos):
            nome = 'Desconhecido'

            if rostos_conhecidos_codificacoes:
                matches = face_recognition.compare_faces(rostos_conhecidos_codificacoes, codificacao_face)
                if True in matches:
                    first_match_index = matches.index(True)
                    nome = nomes_dos_rostos_conhecidos[first_match_index]
            
            current_frame_recognized_names.add(nome)

            top *= 4 
            right *= 4 
            bottom *= 4 
            left *= 4 

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, nome, (left + 6, bottom - 6), font, 0.7, (255, 255, 255), 1)
        global_recognized_faces_in_view = current_frame_recognized_names

        cv2.imshow('Luna: Camera Ativa', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set() 
    video_capture.release()
    cv2.destroyAllWindows()
    print("Câmera desativada.")
    global_recognized_faces_in_view.clear() 


def start_camera():
    global camera_thread, camera_stop_event
    if camera_thread is not None and camera_thread.is_alive():
        speak("A câmera já está ativa, Milleny.")
        return

    speak("Certo, abrindo a câmera. Ficarei de olho no ambiente.")
    camera_stop_event.clear() 

    caminhos_rostos_para_luna = ["milleny_conhecida.jpg"] 
    
    camera_thread = threading.Thread(target=reconhecimento_facial_em_tempo_real_thread, 
                                     args=(camera_stop_event, 0, caminhos_rostos_para_luna))
    camera_thread.start()

def stop_camera():
    global camera_thread, camera_stop_event
    if camera_thread is None or not camera_thread.is_alive():
        speak("A câmera não está ativa, Milleny.")
        return

    speak("Fechando a câmera. Aguarde um momento.")
    camera_stop_event.set() 
    camera_thread.join()
    camera_thread = None 
    speak("Câmera fechada.")


def speak(audio):
    print(f'Luna: {audio}')
    engine.say(audio)
    engine.runAndWait()

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Luna: Ouvindo...")
        r.pause_threshold = 1.2
        audio = r.listen(source)

    try:
        print("Luna: Reconhecendo...")
        query = r.recognize_google(audio, language='pt-br')
        print(f"Você disse: {query}\n")
        return query.lower() 

    except sr.UnknownValueError:
        print('Luna: Desculpe, não entendi o que você disse, fale novamente.')
        return 'none' 
    except sr.RequestError as e: 
        print(f"Luna: Não foi possível solicitar resultados do serviço de fala Google; {e}")
        return "none" 

def ask_gemini(prompt_text):
    print('Luna: só um momento...')
    try:
        full_prompt = (
            "Você é uma assistente pessoal chamada Luna. Sua principal função é responder a perguntas e fornecer informações. "
            "Você NÃO TEM CAPACIDADE de interagir diretamente com o sistema operacional do usuário, como abrir ou fechar programas, "
            "manipular arquivos ou controlar o mouse/teclado. Se for solicitado a realizar uma ação no computador que você não pode fazer, "
            "explique educadamente sua limitação. Seja concisa e útil.\n\n" + prompt_text
        )
        response = gemini_model.generate_content(
            [
                {"role": "user", "parts": [full_prompt]}
            ]
        )
        if response.parts: 
            return response.text
        else:
            return 'Não consegui encontrar uma resposta para isso :('
    except Exception as e:
        print(f'Erro ao chamar API Gemini: {e}')
        return "Desculpe, tive um problema ao acessar o cérebro inteligente no momento. Por favor, tente novamente mais tarde."

def mover_e_clicar(x, y):
    pyautogui.moveTo(x, y, duration=0.5)
    pyautogui.click()

def digitar_texto(texto):
    pyautogui.write(texto)

def pressionar_tecla(tecla):
    pyautogui.press(tecla)

def abrir_bloco_notas():
    pyautogui.press('win')
    pyautogui.sleep(1)
    pyautogui.write('bloco de notas')
    pyautogui.sleep(0.5)
    pyautogui.press('enter')
    speak("Bloco de Notas aberto.")

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
    
def check_command_fuzzy(command_heard, expected_commands, threshold=80):
    for expected in expected_commands:
        if fuzz.ratio(command_heard, expected) >= threshold:
            return True
        if fuzz.partial_ratio(command_heard, expected) >= threshold:
            return True
    return False


if __name__ == '__main__':
    speak("Iniciando assistente. Por favor, aguarde.")
    speak("Olá, eu sou seu assistente pessoal. Diga 'Luna' para me ativar.")

    COMMAND_MAP = {
        "abrir bloco de notas": ["abrir bloco de notas", "iniciar bloco de notas", "abra o bloco de notas", "bloco de notas", "pode abrir o bloco de notas", "abre o bloco de notas", "abrir o bloco de", "abra o bloco", "iniciar o bloco de notas"],
        "abrir discord": ["abrir discord", "iniciar discord", "iniciar o discord", "abra o discord", "pode abrir o discord"],
        "horas": ["horas", "que horas são"],
        "pesquisar no google": ["pesquisar no google", "procurar no google", "google", "busca google"],
        "abrir youtube": ["abrir youtube", "youtube", "iniciar youtube", "ir para o youtube"],
        "pesquisar no youtube": ["pesquisar no youtube", "procurar no youtube", "busca youtube", "youtube pesquisar"],
        
        "abrir câmera": ["abrir câmera", "ativar câmera", "ligar câmera"],
        "fechar câmera": ["fechar câmera", "desativar câmera", "desligar câmera", "parar câmera"],
     
        "quem está aí": ["quem está aí", "quem você vê", "quem é", "me reconhece"], 
    }

    while True:
        query = listen_command()

        if "sair" in query or "desligar" in query:
        
            if camera_thread is not None and camera_thread.is_alive():
                speak("Desativando a câmera antes de encerrar.")
                camera_stop_event.set()
                camera_thread.join()
            speak("Encerrando.")
            break 

        elif 'luna' in query:
            speak('Olá Milleny, como posso te ajudar?')

            command = listen_command()
            print(f"DEBUG - Comando recebido após hotword: {command}") 

            if 'none' in command:
                speak('Desculpe, não entendi o seu comando. Poderia repetir?')
                continue 

            matched_command_type = None
            for cmd_type, variations in COMMAND_MAP.items():
                if check_command_fuzzy(command, variations, threshold=75):
                    matched_command_type = cmd_type
                    break
            
            
            if matched_command_type == "abrir câmera":
                start_camera()

            elif matched_command_type == "fechar câmera":
                stop_camera()
            
            elif matched_command_type == "quem está aí":
                if camera_thread is not None and camera_thread.is_alive():
                    
                    if global_recognized_faces_in_view:
                        known_faces = [name for name in global_recognized_faces_in_view if name != "Desconhecido"]
                        if known_faces:
                            speak(f"Na câmera, vejo: {', '.join(known_faces)}.")
                        else:
                            speak("Vejo rostos, mas nenhum conhecido no momento.")
                    else:
                        speak("Não vejo nenhum rosto na câmera no momento.")
                else:
                    speak("A câmera não está ativa para eu poder ver.")

            
            elif matched_command_type == "abrir bloco de notas":
                speak("Certo, abrindo o Bloco de Notas.") 
                abrir_bloco_notas()

            elif matched_command_type == "abrir discord":
                speak("Entendido, abrindo o Discord.") 
                abrir_discord()

            elif matched_command_type == "horas":
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak(f"Senhorita, são {strTime}") 

            elif matched_command_type == "pesquisar no google":
                speak('O que a senhorita gostaria de pesquisar no Google hoje?')
                search_query = listen_command()
                if search_query != 'none':
                    speak(f"Pesquisando por {search_query} no Google.")
                    webbrowser.open(f"https://www.google.com/search?q={search_query}")
                else:
                    speak("Não entendi o que pesquisar.")

            elif matched_command_type == "abrir youtube":
                speak("Abrindo YouTube.")
                webbrowser.open("https://www.youtube.com/") 

            elif matched_command_type == "pesquisar no youtube":
                speak('O que a senhorita gostaria de pesquisar no YouTube hoje?')
                search_query = listen_command()
                if search_query != 'none':
                    speak(f"Pesquisando por {search_query} no YouTube.")
                    webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}") 
                else:
                    speak("Não entendi o que pesquisar no YouTube.")

            else: 
                speak("Deixe-me pensar...")
                response_from_gemini = ask_gemini(command) 
                speak(response_from_gemini)

                
                in_gemini_conversation = True
                while in_gemini_conversation:
                    speak("Algo mais que eu possa te ajudar, Milleny?") 
                    next_command = listen_command() 
                    print(f"DEBUG - Comando recebido na conversa Gemini: {next_command}")

                    if "sair da conversa" in next_command or "parar de conversar" in next_command or "chega" in next_command:
                        speak("Ok, voltando ao modo de escuta geral. Diga 'Luna' para me reativar.")
                        in_gemini_conversation = False 
                    elif "sair" in next_command or "desligar" in next_command:
                        
                        if camera_thread is not None and camera_thread.is_alive():
                            speak("Desativando a câmera antes de encerrar.")
                            camera_stop_event.set()
                            camera_thread.join()
                        speak("Encerrando.")
                        in_gemini_conversation = False 
                        break 
                    elif next_command == 'none':
                        speak("Não entendi. Poderia repetir?")
                   
                    elif check_command_fuzzy(next_command, COMMAND_MAP["abrir câmera"], threshold=75):
                        start_camera()
                    elif check_command_fuzzy(next_command, COMMAND_MAP["fechar câmera"], threshold=75):
                        stop_camera()
                    elif check_command_fuzzy(next_command, COMMAND_MAP["quem está aí"], threshold=75):
                        if camera_thread is not None and camera_thread.is_alive():
                            if global_recognized_faces_in_view:
                                known_faces = [name for name in global_recognized_faces_in_view if name != "Desconhecido"]
                                if known_faces:
                                    speak(f"Na câmera, vejo: {', '.join(known_faces)}.")
                                else:
                                    speak("Vejo rostos, mas nenhum conhecido no momento.")
                            else:
                                speak("Não vejo nenhum rosto na câmera no momento.")
                        else:
                            speak("A câmera não está ativa para eu poder ver.")
                    else:
                        speak("Só um momento...")
                        response_from_gemini = ask_gemini(next_command)
                        speak(response_from_gemini)