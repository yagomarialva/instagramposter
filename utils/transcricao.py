import os

def ferramenta_ler_arquivo(caminho_arquivo):
    """Lê o conteúdo de um arquivo de texto se ele existir."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        return None

def ferramenta_salvar_arquivo(caminho_arquivo, conteudo):
    """Salva conteúdo em um arquivo de texto."""
    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)

def openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client):
    """Transcreve um arquivo de áudio usando Whisper da OpenAI."""
    caminho_arquivo_txt = f"transcricoes/texto_completo_{nome_arquivo}.txt"

    if transcricao := ferramenta_ler_arquivo(caminho_arquivo_txt):
        print("Transcrição já existe. Pulando a transcrição...")
        return transcricao
    
    print("Transcrevendo o áudio com o OpenAI...")
    with open(caminho_audio, "rb") as audio:
        response = client.audio.transcriptions.create(model=modelo_whisper, file=audio)
    
    transcricao_completa = response.text.strip()
    ferramenta_salvar_arquivo(caminho_arquivo_txt, transcricao_completa)
    return transcricao_completa
