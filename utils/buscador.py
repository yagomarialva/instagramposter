import os
import time
import requests
from googlesearch import search
from bs4 import BeautifulSoup
from newspaper import Article
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment
from io import BytesIO
import pyttsx3

def criar_pasta(pasta):
    """Cria a pasta se ela não existir, agora com caminho absoluto ou relativo."""
    if not os.path.exists(pasta):
        os.makedirs(pasta)

def buscar_noticias(termo, num_resultados=50):
    """Busca links de notícias relevantes no Google."""
    print(f"🔍 Buscando notícias sobre: {termo}...")
    query = f"{termo} notícia"
    resultados = search(query, num_results=num_resultados, lang="pt")
    
    # Filtrando apenas links que realmente são artigos de notícias
    links_filtrados = [url for url in resultados if "news.google.com" not in url and "/search?" not in url]
    
    return links_filtrados[:num_resultados]

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
    pasta = "../noticias"  # Caminho absoluto ou relativo fora da pasta do script
    criar_pasta(pasta)
    
    intro = "Bem-vindo ao podcast de ufologia. Aqui estão as notícias mais recentes sobre fenômenos ufológicos!"
    
    for idx, noticia in enumerate(noticias, 1):
        # Verifica se a notícia tem pelo menos 500 palavras
        conteudo_noticia = noticia['conteudo']
        num_palavras = len(conteudo_noticia.split())
        
        if num_palavras >= 200:
            # Nome do arquivo baseado no título da notícia (removendo caracteres especiais)
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

def gerar_podcast(texto, nome_arquivo):
    """Converte o texto em fala e salva como arquivo MP3 em um diretório fora do script."""
    pasta = "../podcasts"  # Caminho absoluto ou relativo fora da pasta do script
    criar_pasta(pasta)
    nome_arquivo_podcast = os.path.join(pasta, nome_arquivo)

    try:
        tts = gTTS(text=texto, lang='pt')
        
        tts.save('temp_audio.mp3')        
        audio = AudioSegment.from_mp3('temp_audio.mp3')        
        audio.export(nome_arquivo_podcast, format="mp3")
        
        print(f"🎧 Podcast salvo como: {nome_arquivo_podcast}")
    except Exception as e:
        print(f"⚠️ Erro ao gerar o podcast: {e}")


def gerar_podcast_para_noticias(noticias):
    print("\n🎙️ Gerando podcasts para as notícias...")
    """Gera podcasts para todas as notícias extraídas."""
    
    intro = "Bem-vindo ao podcast de ufologia. Aqui estão as notícias mais recentes sobre fenômenos ufológicos!\n\n"
    
    for idx, noticia in enumerate(noticias, 1):
        titulo = noticia['titulo']
        conteudo = noticia['conteudo']
        
        texto_podcast = f"{intro}{titulo}\n\n{conteudo}"
        
        nome_arquivo_podcast = f"podcast_noticia_{idx}_{titulo}.mp3"
        
        gerar_podcast(texto_podcast, nome_arquivo_podcast)


if __name__ == "__main__":
    termo_pesquisa = input("Digite o termo para buscar notícias: ")
    links_noticias = buscar_noticias(termo_pesquisa)
    
    noticias_extraidas = []
    for link in links_noticias:
        print(f"📄 Extraindo: {link}")
        noticia = extrair_noticia(link)
        if noticia:
            noticias_extraidas.append(noticia)

    salvar_em_txt_individual(termo_pesquisa, noticias_extraidas)
    
    gerar_podcast_para_noticias(noticias_extraidas)
