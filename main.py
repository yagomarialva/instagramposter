import openai
from dotenv import load_dotenv
import os

def openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client):
    print("Transcrevendo o áudio com o OpenAI")
    
    with open(caminho_audio, "rb") as audio:
        response = client.audio.transcriptions.create(
            model=modelo_whisper,
            file=audio
        )
    
    transcricao_completa = response.text  # A nova API retorna um objeto, e o texto fica em `.text`
    
    with open(f"texto_completo_{nome_arquivo}.txt", "w", encoding="utf-8") as arquivo_texto:
        arquivo_texto.write(transcricao_completa)

    return transcricao_completa

def main():
    load_dotenv()
    
    caminho_audio = "podcasts/hipsters_154_testes_short.mp3"
    nome_arquivo = "hipsters_154_testes_short"
    
    api_openai = os.getenv("API_KEY_OPENAI")
    client = openai.Client(api_key=api_openai)  # Criando um cliente OpenAI
    
    modelo_whisper = "whisper-1"
    
    transcricao_completa = openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client)
    
if __name__ == "__main__":
    main()
