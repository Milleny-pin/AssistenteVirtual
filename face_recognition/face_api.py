import face_recognition
import cv2
import numpy as np
import threading
from config.settings import camera_thread, camera_stop_event, global_recognized_faces_in_view
from services.voice_service import speak

def reconhecimento_facial_em_tempo_real_thread(stop_event, cam_index=0, cam_known_faces_paths=None):
    """
    Função principal de reconhecimento facial que roda em um thread separado.
    """
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
    """Inicia o thread de reconhecimento facial."""
    global camera_thread, camera_stop_event
    if camera_thread is not None and camera_thread.is_alive():
        speak("A câmera já está ativa, Milleny.")
        return

    speak("Certo, abrindo a câmera. Ficarei de olho no ambiente.")
    camera_stop_event.clear()

   
    caminhos_rostos_para_luna = ["../assets/milleny_conhecida.jpg"] 
    
 
    camera_thread = threading.Thread(target=reconhecimento_facial_em_tempo_real_thread,
                                     args=(camera_stop_event, 0, caminhos_rostos_para_luna))
    camera_thread.start()

def stop_camera():
    """Para o thread de reconhecimento facial."""
    global camera_thread, camera_stop_event
    if camera_thread is None or not camera_thread.is_alive():
        speak("A câmera não está ativa, Milleny.")
        return

    speak("Fechando a câmera. Aguarde um momento.")
    camera_stop_event.set()
    camera_thread.join()
   
    globals()['camera_thread'] = None 
    speak("Câmera fechada.")