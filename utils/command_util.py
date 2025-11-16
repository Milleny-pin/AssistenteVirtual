from fuzzywuzzy import fuzz

# Mapeamento de comandos
COMMAND_MAP = {
    'abrir spotify': ['abrir spotify', 'iniciar spotify','vamos procurar uma música', 'quero ouvir música',],
    "abrir bloco de notas": ["abrir bloco de notas", "iniciar bloco de notas", "abra o bloco de notas", "bloco de notas", "pode abrir o bloco de notas", "abre o bloco de notas", "abrir o bloco de", "abra o bloco", "iniciar o bloco de notas"],
    "abrir discord": ["abrir discord", "iniciar discord", "iniciar o discord", "abra o discord", "pode abrir o discord"],
    "horas": ["horas", "que horas são"],
    "pesquisar no google": ["pesquisar no google", "procurar no google", "google", "busca google"],
    "abrir youtube": ["abrir youtube", "youtube", "iniciar youtube", "ir para o youtube"],
    "pesquisar no youtube": ["pesquisar no youtube", "procurar no youtube", "busca youtube", "youtube pesquisar"],
    
    "abrir câmera": ["abrir câmera", "ativar câmera", "ligar câmera"],
    "fechar câmera": ["fechar câmera", "desativar câmera", "desligar câmera", "parar câmera"],
    
    "quem está aí": ["quem está aí", "quem você vê", "quem é", "me reconhece"],
   "ligar tv": ["ligar tv", "liga a tv", "tv liga"],
   "aumentar_volume":["aumentar volume da tv", "aumentar volume da televisão", "aumentar volume da tv por favor"]


}

# -----------------------------------------------------------------
# --- FUNÇÃO DE VERIFICAÇÃO DE COMANDOS FUZZY ---
# -----------------------------------------------------------------

def check_command_fuzzy(command_input, command_map, threshold=70):
    """
    Verifica o comando de entrada (falado) contra o mapa de comandos usando
    lógica de correspondência fuzzy (similaridade de string).
    
    :param command_input: O texto do comando que o usuário falou (em minúsculas).
    :param command_map: O dicionário de mapeamento de comandos (COMMAND_MAP).
    :param threshold: Pontuação mínima (0-100) para ser considerada uma correspondência.
    :return: A chave do comando correspondente (ex: "ligar tv") ou 'none'.
    """
    
    # Converte o comando de entrada para minúsculas e remove espaços extras
    command_input = command_input.lower().strip()
    
    best_match_score = 0
    best_match_key = "none"

    # Itera sobre cada tipo de comando (ex: "ligar tv") e suas variações (ex: ["ligar tv", "desligar tv"])
    for key, variations in command_map.items():
        for variation in variations:
            # Calcula a similaridade entre a entrada do usuário e a variação
            score = fuzz.ratio(command_input, variation)
            
            # Se a pontuação for a melhor que encontramos até agora E acima do limite
            if score > best_match_score and score >= threshold:
                best_match_score = score
                best_match_key = key
                
    # DEBUG: Para ajudar a ver as pontuações de similaridade:
    # print(f"DEBUG - Melhor comando fuzzy correspondente: {best_match_key} com pontuação: {best_match_score}")
    
    return best_match_key

# Função vazia (mock) para garantir que a importação do app.py não falhe
# Caso você não tenha esta função, remova-a, mas ela é comum em projetos grandes
def get_command_map():
    return COMMAND_MAP