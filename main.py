import os
from openai import OpenAI
from dotenv import load_dotenv

def ferramenta_ler_arquivo(nome_arquivo):
    """Lê o conteúdo de um arquivo de texto se ele existir."""
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado. Criando um novo...")
        return None
    except IOError as e:
        print(f"Erro ao carregar o arquivo {nome_arquivo}: {e}")
        return None

def openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client):
    """Transcreve um arquivo de áudio usando Whisper da OpenAI, caso a transcrição ainda não exista."""
    nome_arquivo_txt = f"texto_completo_{nome_arquivo}.txt"

    transcricao_existente = ferramenta_ler_arquivo(nome_arquivo_txt)
    if transcricao_existente:
        print("Arquivo de transcrição encontrado. Pulando a transcrição...")
        return transcricao_existente

    print("Transcrevendo o áudio com o OpenAI...")

    with open(caminho_audio, "rb") as audio:
        response = client.audio.transcribe(
            model=modelo_whisper,
            file=audio
        )
    
    transcricao_completa = response.text.strip()

    with open(nome_arquivo_txt, "w", encoding="utf-8") as arquivo_texto:
        arquivo_texto.write(transcricao_completa)

    return transcricao_completa

def openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, client):
    """Gera um resumo da transcrição para um post no Instagram, caso ainda não exista."""
    nome_resumo_txt = f"resumo_instagram_{nome_arquivo}.txt"

    resumo_existente = ferramenta_ler_arquivo(nome_resumo_txt)
    if resumo_existente:
        print("Arquivo de resumo encontrado. Pulando a geração do resumo...")
        return resumo_existente

    print("Resumindo com o GPT para um post do Instagram...")

    prompt_sistema = """
    Assuma que você é um digital influencer da área de tecnologia e que está criando conteúdos para um podcast.

    Os textos devem considerar:
    - Seguidores são entusiastas de tecnologia e computação.
    - Uso do gênero neutro.
    - Texto deve ser um convite para ouvir o podcast no Instagram.
    - Texto em português do Brasil.
    """

    prompt_usuario = f'Aqui está uma transcrição: "{transcricao_completa}". Por favor, reescreva como uma legenda chamativa para o Instagram, incluindo hashtags.'

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.6
    )

    resumo_instagram = resposta.choices[0].message.content.strip()

    with open(nome_resumo_txt, "w", encoding="utf-8") as arquivo_texto:
        arquivo_texto.write(resumo_instagram)

    return resumo_instagram

def openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, client):
    """Gera um texto curto para a criação de imagens com base no resumo."""
    nome_texto_imagem = f"texto_para_geracao_imagem_{nome_arquivo}.txt"

    texto_existente = ferramenta_ler_arquivo(nome_texto_imagem)
    if texto_existente:
        print("Arquivo de texto para imagem encontrado. Pulando a geração...")
        return texto_existente

    print("Gerando a saída de texto para criação de imagens com o GPT ...")

    prompt_sistema = """
    - A saída deve ser uma única frase do tamanho de um tweet, que descreva o conteúdo do texto de forma impactante para ser transcrita como uma imagem.
    - Não inclua hashtags.
    """

    prompt_usuario = f'Reescreva o texto a seguir como uma frase curta e chamativa para um post de imagem: "{resumo_instagram}"'

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.6
    )

    texto_para_imagem = resposta.choices[0].message.content.strip()

    with open(nome_texto_imagem, "w", encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(texto_para_imagem)

    return texto_para_imagem

def openai_dalle_gerar_imagem(resolucao, resumo_para_imagem, nome_arquivo, client, quantidade=1):
    """Gera uma imagem com base no texto fornecido."""
    print("Gerando imagem com o DALL-E...")

    prompt_user = "Uma pintura ultra futurista, textless, de um cenário tecnológico com elementos de computação e tecnologia. A imagem deve ser quadrada e ter uma resolução de 1024x1024." + resumo_para_imagem
    
    resposta = client.images.generate(
        model="dall-e-3",
        prompt=prompt_user,
        n=quantidade,
        size=resolucao
    )

    # Corrigindo o acesso ao atributo correto
    url_imagem = resposta.data[0].url
    print(f"Imagem gerada! URL: {url_imagem}")

    return url_imagem

def main():
    """Executa todo o fluxo de transcrição, resumo e geração de texto para imagens."""
    load_dotenv()
    
    caminho_audio = "podcasts/hipsters_154_testes_short.mp3"
    nome_arquivo = "hipsters_154_testes_short"
    resolucao = "1024x1024"
    
    api_openai = os.getenv("API_KEY_OPENAI")
    client = OpenAI(api_key=api_openai)
    
    modelo_whisper = "whisper-1"
    
    transcricao_completa = openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client)
    resumo_instagram = openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, client)
    texto_para_imagem = openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, client)
    resumo_imagem_instagram = ferramenta_ler_arquivo(f"texto_para_geracao_imagem_{nome_arquivo}.txt")

    imagem_gerada = openai_dalle_gerar_imagem(resolucao,resumo_imagem_instagram,nome_arquivo,client)
if __name__ == "__main__":
    main()
