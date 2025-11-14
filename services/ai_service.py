# Importar o modelo configurado no settings
from config.settings import gemini_model 
#from jarvis_env.services.voice_service import speak # Para que as funções dentro deste arquivo usem speak

def ask_gemini(prompt_text):
    """Envia um prompt ao modelo Gemini e retorna a resposta."""
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
        
        if response.text: 
            return response.text
        else:
            return 'Não consegui encontrar uma resposta para isso. Tente refinar sua pergunta.'
            
    except gemini_types.APIError as e:
       
        print(f'Erro da API Gemini: {e}')
        return "Desculpe, tive um problema de comunicação com a inteligência artificial (erro de API). Por favor, tente novamente."
        
    except Exception as e:
        
        print(f'Erro inesperado: {e}')
        return "Desculpe, tive um problema técnico inesperado e não consegui processar seu pedido. Tente novamente mais tarde."