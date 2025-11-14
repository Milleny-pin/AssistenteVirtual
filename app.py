import os
import sys
# Não precisa de 'from fuzzywuzzy import fuzz' aqui se já está em command_util

# Obtém o caminho absoluto do diretório onde o app.py está 
current_dir = os.path.dirname(os.path.abspath(__file__))

# Adiciona o diretório principal do projeto ao sys.path.
sys.path.append(current_dir)

# --- Importações de Módulos (Corrigidas para refletir 'jarvis_env') ---
from .config.settings import camera_thread, camera_stop_event, global_recognized_faces_in_view
from services.tv_control import ligar_desligar
from services.voice_service import speak, listen_command
from services.ai_service import ask_gemini
from services.os_control import abrir_spotify, abrir_discord, abrir_bloco_notas, search_google, search_youtube, open_youtube, get_current_time
from face_recognition.face_api import start_camera, stop_camera
from utils.command_util import COMMAND_MAP, check_command_fuzzy



if __name__ == '__main__':
    speak("Iniciando assistente. Por favor, aguarde.")
    speak("Olá, eu sou seu assistente pessoal. Diga 'Luna' para me ativar.")

    while True:
        # Aumenta/diminui o timeout da escuta se a câmera estiver ativa
        if camera_thread is not None and camera_thread.is_alive():
            query = listen_command(timeout_duration=3)
            if query == "none_timeout":
                continue
        else:
            query = listen_command(timeout_duration=5)

        # 1. Comando de SAÍDA/DESLIGAR (Executado se 'sair' ou 'desligar' estiver em 'query')
        if "sair" in query or "desligar" in query:
            if camera_thread is not None and camera_thread.is_alive():
                speak("Desativando a câmera antes de encerrar.")
                camera_stop_event.set()
                camera_thread.join()
            speak("Encerrando.")
            break

        # 2. Hotword de ATIVAÇÃO
        elif 'luna' in query:
            speak('Olá Milleny, como posso te ajudar?')
            
            # Escuta o comando após a hotword
            command = listen_command(timeout_duration=5 if camera_thread is not None and camera_thread.is_alive() else None)
            print(f"DEBUG - Comando recebido após hotword: {command}")

            if 'none' in command or 'none_timeout' in command:
                speak('Desculpe, não entendi o seu comando. Poderia repetir?')
                continue

            # 3. Mapeamento e Despacho de Comandos
            
            matched_command_type = check_command_fuzzy(command, COMMAND_MAP)
            
            # DEBUG CRÍTICO: Mostra o tipo de comando que será executado.
            print(f"DEBUG - Tipo de comando correspondente: {matched_command_type}") 
            
            # --- EXECUÇÃO DE FUNÇÕES (Despacho de Comandos) ---
            
            # --- 1. COMANDOS DE CONTROLE DA TV ---
            if matched_command_type == "ligar tv":
                speak("Comando da TV recebido. Vou tentar ligar ou desligar.")
                ligar_desligar()

            elif matched_command_type == "aumentar volume":
                speak("Aumentando o volume da TV.")
             
                pass

            # --- 2. COMANDOS DE CÂMERA E RECONHECIMENTO FACIAL ---
            elif matched_command_type == "abrir câmera":
                speak("Abrindo a câmera.")
                start_camera()

            elif matched_command_type == "fechar câmera":
                speak("Fechando a câmera.")
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

            # --- 3. COMANDOS DE CONTROLE DO SISTEMA/APLICATIVOS ---
            elif matched_command_type == "abrir bloco de notas":
                speak("Certo, abrindo o Bloco de Notas.")
                abrir_bloco_notas()

            elif matched_command_type == "abrir spotify":
                speak("Entendido, abrindo o Spotify.")
                abrir_spotify()

            elif matched_command_type == "abrir discord":
                speak("Entendido, abrindo o Discord.")
                abrir_discord()

            # --- 4. COMANDOS DE INFORMAÇÃO E BUSCA ---
            elif matched_command_type == "horas":
                get_current_time()

            elif matched_command_type == "pesquisar no google":
                speak('O que a senhorita gostaria de pesquisar no Google hoje?')
                search_query = listen_command(timeout_duration=5 if camera_thread is not None and camera_thread.is_alive() else None)
                if search_query != 'none' and search_query != 'none_timeout':
                    speak(f"Pesquisando por {search_query} no Google.")
                    search_google(search_query)
                else:
                    speak("Não entendi o que pesquisar.")

            elif matched_command_type == "abrir youtube":
                speak("Abrindo YouTube.")
                open_youtube()

            elif matched_command_type == "pesquisar no youtube":
                speak('O que a senhorita gostaria de pesquisar no YouTube hoje?')
                search_query = listen_command(timeout_duration=5 if camera_thread is not None and camera_thread.is_alive() else None)
                if search_query != 'none' and search_query != 'none_timeout':
                    speak(f"Pesquisando por {search_query} no YouTube.")
                    search_youtube(search_query)
                else:
                    speak("Não entendi o que pesquisar no YouTube.")

            # --- 5. COMANDO GENÉRICO (CHAMA GEMINI) ---
            else:
                speak("Deixe-me pensar...")
                response_from_gemini = ask_gemini(command)
                speak(response_from_gemini)

            
                in_gemini_conversation = True
                while in_gemini_conversation:
                    speak("Algo mais que eu possa te ajudar, Milleny?")
                    next_command = listen_command(timeout_duration=5 if camera_thread is not None and camera_thread.is_alive() else None)
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
                    elif next_command == 'none' or next_command == 'none_timeout':
                        speak("Não entendi. Poderia repetir?")
                    
                    # Permite comandos de câmera DENTRO da conversa Gemini
                    elif check_command_fuzzy(next_command, COMMAND_MAP, threshold=75) == "abrir câmera":
                        start_camera()
                    elif check_command_fuzzy(next_command, COMMAND_MAP, threshold=75) == "fechar câmera":
                        stop_camera()
                    elif check_command_fuzzy(next_command, COMMAND_MAP, threshold=75) == "quem está aí":
                        if camera_thread is not None and camera_thread.is_alive():
                            pass # Substituir este 'pass' pela  lógica completa
                        else:
                            speak("A câmera não está ativa para eu poder ver.")
                    else:
                        speak("Só um momento...")
                        response_from_gemini = ask_gemini(next_command)
                        speak(response_from_gemini)