import os
import time
import base64
import requests
from openai import OpenAI
from dotenv import load_dotenv
from googlesearch import search
from bs4 import BeautifulSoup
from newspaper import Article

def criar_pasta(pasta):
    """Cria a pasta se ela não existir."""
    if not os.path.exists(pasta):
        os.makedirs(pasta)

def buscar_noticias(termo, num_resultados=3):
    """Busca links relevantes no Google (não apenas notícias)."""
    print(f"🔍 Buscando no Google sobre: {termo}...")
    
    # Remove o filtro 'notícia' para buscar em todo o Google
    resultados = search(termo, num_results=num_resultados, lang="pt")

    # Filtra links duplicados e irrelevantes
    links_filtrados = set(resultados)  # Remove duplicatas automaticamente

    print(f"✅ {len(links_filtrados)} resultados encontrados.")
    return list(links_filtrados)[:num_resultados]

def extrair_noticia(url):
    """Extrai título, data e conteúdo completo da notícia."""
    try:
        article = Article(url)
        article.download()
        article.parse()

        titulo = article.title if article.title else "Sem título"
        data_publicacao = article.publish_date.strftime("%d/%m/%Y %H:%M") if article.publish_date else "Data não encontrada"
        conteudo = article.text if article.text else "Conteúdo não encontrado"

        return {
            "titulo": titulo,
            "data": data_publicacao,
            "url": url,
            "conteudo": conteudo
        }
    except Exception as e:
        print(f"⚠️ Erro ao extrair notícia de {url}: {e}")
        return None

def salvar_em_txt_individual(termo, noticias):
    """Salva cada notícia em um arquivo de texto individual em uma pasta fora do diretório atual."""
    pasta = "../noticias"
    criar_pasta(pasta)

    intro = "Bem-vindo ao podcast de ufologia. Aqui estão as notícias mais recentes sobre fenômenos ufológicos!"

    for idx, noticia in enumerate(noticias, 1):
        # Verifica se a notícia tem pelo menos 200 palavras
        conteudo_noticia = noticia['conteudo']
        num_palavras = len(conteudo_noticia.split())

        if num_palavras >= 200:
            # Nome do arquivo baseado no título da notícia
            nome_arquivo = f"noticia_{idx}_{noticia['titulo'].replace(' ', '_').replace('/', '-')}.txt"
            caminho_arquivo = os.path.join(pasta, nome_arquivo)

            with open(caminho_arquivo, "w", encoding="utf-8") as file:
                file.write(f"📰 Notícia sobre: {termo}\n")
                file.write("=" * 80 + "\n\n")
                file.write(f"{intro}\n\n")
                file.write(f"{noticia['titulo']}\n")
                file.write(f"📅 Data: {noticia['data']}\n")
                file.write(f"🔗 Link: {noticia['url']}\n\n")
                file.write(f"{noticia['conteudo']}\n")
                file.write("=" * 80 + "\n\n")
                time.sleep(2)  # Evita bloqueios

            print(f"\n✅ Arquivo salvo como: {caminho_arquivo}")
        else:
            print(f"⚠️ A notícia '{noticia['titulo']}' não tem 200 palavras e foi ignorada.")

def gerar_podcast_openai(texto, nome_arquivo, client):
    """Converte o texto em fala usando OpenAI e salva como arquivo WAV."""
    pasta = "../podcasts"
    criar_pasta(pasta)

    try:
        print("🎙️ Gerando podcast com a IA da OpenAI...")

        completion = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "echo", "format": "wav"},
            messages=[{"role": "user", "content": texto}]
        )

        # Decodifica o áudio gerado
        wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)

        # Caminho para salvar o podcast
        nome_arquivo_podcast = os.path.join(pasta, f"{nome_arquivo}.wav")

        with open(nome_arquivo_podcast, "wb") as f:
            f.write(wav_bytes)

        print(f"✅ Podcast gerado e salvo em: {nome_arquivo_podcast}")
    except Exception as e:
        print(f"❌ Erro ao gerar o podcast: {e}")

def gerar_podcast_para_noticias(noticias, client):
    """Gera podcasts para todas as notícias usando a IA da OpenAI."""
    print("\n🎙️ Gerando podcasts com IA para as notícias...")

    intro = "Bem-vindo ao podcast de ufologia. Aqui estão as notícias mais recentes sobre fenômenos ufológicos!\n\n"

    for idx, noticia in enumerate(noticias, 1):
        titulo = noticia['titulo']
        conteudo = noticia['conteudo']

        texto_podcast = f"{intro}{titulo}\n\n{conteudo}"
        nome_arquivo_podcast = f"podcast_noticia_{idx}_{titulo.replace(' ', '_').replace('/', '-')}"
        
        gerar_podcast_openai(texto_podcast, nome_arquivo_podcast, client)

if __name__ == "__main__":
    load_dotenv()
    api_openai = os.getenv("API_KEY_OPENAI")
    client = OpenAI(api_key=api_openai)

    termo_pesquisa = input("Digite o termo para buscar notícias: ")
    links_noticias = buscar_noticias(termo_pesquisa)

    noticias_extraidas = []
    for link in links_noticias:
        print(f"📄 Extraindo: {link}")
        noticia = extrair_noticia(link)
        if noticia:
            noticias_extraidas.append(noticia)

    salvar_em_txt_individual(termo_pesquisa, noticias_extraidas)

    # Gera podcasts com OpenAI
    gerar_podcast_para_noticias(noticias_extraidas, client)
