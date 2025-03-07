import os
from openai import OpenAI
from dotenv import load_dotenv
import requests

# Criar diretórios se não existirem
PASTAS = {
    "transcricoes": "transcricoes",
    "resumos": "resumos_instagram",
    "imagens": "imagens"
}

for pasta in PASTAS.values():
    os.makedirs(pasta, exist_ok=True)

def ferramenta_ler_arquivo(caminho_arquivo):
    """Lê o conteúdo de um arquivo de texto se ele existir."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        return None
    except IOError as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

def ferramenta_salvar_arquivo(caminho_arquivo, conteudo):
    """Salva conteúdo em um arquivo de texto."""
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar o arquivo {caminho_arquivo}: {e}")

def openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client):
    """Transcreve um arquivo de áudio usando Whisper da OpenAI, caso a transcrição ainda não exista."""
    caminho_arquivo_txt = os.path.join(PASTAS["transcricoes"], f"texto_completo_{nome_arquivo}.txt")

    if transcricao := ferramenta_ler_arquivo(caminho_arquivo_txt):
        print("Transcrição já existe. Pulando a transcrição...")
        return transcricao
    
    print("Transcrevendo o áudio com o OpenAI...")
    with open(caminho_audio, "rb") as audio:
        response = client.audio.transcriptions.create(
            model=modelo_whisper,
            file=audio
        )
    
    transcricao_completa = response.text.strip()
    ferramenta_salvar_arquivo(caminho_arquivo_txt, transcricao_completa)
    return transcricao_completa

def openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, client):
    """Gera um resumo da transcrição para um post no Instagram, caso ainda não exista."""
    caminho_resumo_txt = os.path.join(PASTAS["resumos"], f"resumo_instagram_{nome_arquivo}.txt")

    if resumo := ferramenta_ler_arquivo(caminho_resumo_txt):
        print("Resumo já existe. Pulando a geração...")
        return resumo

    print("Resumindo com o GPT...")
    prompt_sistema = """
    Assuma que você é um digital influencer da área de tecnologia criando conteúdos para um podcast.
    - Use gênero neutro
    - Convide para ouvir o podcast
    - Texto em português do Brasil
    """
    prompt_usuario = f'Reescreva como uma legenda chamativa para Instagram: "{transcricao_completa}".'

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.6
    )

    resumo_instagram = resposta.choices[0].message.content.strip()
    ferramenta_salvar_arquivo(caminho_resumo_txt, resumo_instagram)
    return resumo_instagram

def openai_dalle_gerar_imagem(resumo_para_imagem, nome_arquivo, client, quantidade):
    """Gera imagens com base no texto, caso ainda não existam."""
    caminhos_imagens = [os.path.join(PASTAS["imagens"], f"{nome_arquivo}_{i}.png") for i in range(quantidade)]

    if all(os.path.exists(img) for img in caminhos_imagens):
        print("Imagens já existem. Pulando geração...")
        return caminhos_imagens

    print("Gerando imagens com DALL-E...")
    prompt_user = f"Uma pintura futurista e misteriosa, textless, 3D que retrate: {resumo_para_imagem}."

    imagens_geradas = [client.images.generate(
        model="dall-e-3",
        prompt=prompt_user,
        n=1,
        size="1024x1024"
    ).data[0].url for _ in range(quantidade)]

    for i, url in enumerate(imagens_geradas):
        imagem = requests.get(url)
        with open(caminhos_imagens[i], "wb") as arquivo:
            arquivo.write(imagem.content)

    return caminhos_imagens

def main():
    """Executa todo o fluxo de transcrição, resumo e geração de imagem."""
    load_dotenv()
    caminho_audio = "podcasts/hipsters_154_testes_short.mp3"
    nome_arquivo = "hipsters_154_testes_short"
    api_openai = os.getenv("API_KEY_OPENAI")
    client = OpenAI(api_key=api_openai)

    transcricao = openai_whisper_transcrever(caminho_audio, nome_arquivo, "whisper-1", client)
    resumo = openai_gpt_resumir_texto(transcricao, nome_arquivo, client)
    openai_dalle_gerar_imagem(resumo, nome_arquivo, client, 4)

if __name__ == "__main__":
    main()
