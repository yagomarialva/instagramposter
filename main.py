import os
import whisper
import requests
from dotenv import load_dotenv
from transformers import pipeline
from diffusers import StableDiffusionPipeline

# Criar pastas se não existirem
PASTAS = ["resumos", "transcricoes", "imagens"]
for pasta in PASTAS:
    os.makedirs(pasta, exist_ok=True)

def ferramenta_ler_arquivo(nome_arquivo):
    """Lê o conteúdo de um arquivo de texto se ele existir."""
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        return None
    except IOError as e:
        print(f"Erro ao carregar o arquivo {nome_arquivo}: {e}")
        return None

def ferramenta_salvar_arquivo(nome_arquivo, conteudo):
    """Salva conteúdo em um arquivo de texto."""
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar o arquivo {nome_arquivo}: {e}")

def whisper_transcrever(caminho_audio, nome_arquivo):
    """Transcreve um arquivo de áudio usando Whisper Offline."""
    nome_arquivo_txt = f"transcricoes/{nome_arquivo}.txt"
    
    if transcricao := ferramenta_ler_arquivo(nome_arquivo_txt):
        print("Transcrição já existe. Pulando a transcrição...")
        return transcricao
    
    print("Transcrevendo o áudio com Whisper Offline...")
    modelo = whisper.load_model("small")
    resultado = modelo.transcribe(caminho_audio)
    
    transcricao_completa = resultado["text"].strip()
    ferramenta_salvar_arquivo(nome_arquivo_txt, transcricao_completa)
    return transcricao_completa

def mistral_resumir_texto(transcricao_completa, nome_arquivo):
    """Gera um resumo da transcrição para um post no Instagram usando Mistral 7B."""
    nome_resumo_txt = f"resumos/{nome_arquivo}.txt"
    
    if resumo := ferramenta_ler_arquivo(nome_resumo_txt):
        print("Resumo já existe. Pulando a geração...")
        return resumo
    
    print("Resumindo com Mistral 7B...")
    resumidor = pipeline("summarization", model="mistralai/Mistral-7B-Instruct-v0.1")
    
    resposta = resumidor(transcricao_completa, max_length=50, min_length=20, do_sample=False)
    resumo_instagram = resposta[0]["summary_text"].strip()
    
    ferramenta_salvar_arquivo(nome_resumo_txt, resumo_instagram)
    return resumo_instagram

def stable_diffusion_gerar_imagem(descricao, nome_arquivo):
    """Gera imagens com base no texto usando Stable Diffusion."""
    imagem_salva = f"imagens/{nome_arquivo}.png"
    
    if os.path.exists(imagem_salva):
        print("Imagem já existe. Pulando geração...")
        return imagem_salva
    
    print("Gerando imagem com Stable Diffusion...")
    modelo = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    modelo.to("cpu")  # Troque para "cuda" se tiver GPU
    
    imagem = modelo(descricao).images[0]
    imagem.save(imagem_salva)
    
    return imagem_salva

def main():
    """Executa todo o fluxo de transcrição, resumo e geração de imagem."""
    load_dotenv()
    caminho_audio = "podcasts/hipsters_154_testes_short.mp3"
    nome_arquivo = "hipsters_154_testes_short"
    
    transcricao = whisper_transcrever(caminho_audio, nome_arquivo)
    resumo = mistral_resumir_texto(transcricao, nome_arquivo)
    stable_diffusion_gerar_imagem(resumo, nome_arquivo)

if __name__ == "__main__":
    main()
