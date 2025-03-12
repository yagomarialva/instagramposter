import os
import time
import requests
from bs4 import BeautifulSoup
from newspaper import Article

# URL base da seção Brasil
BASE_URL = "https://marxismo.org.br/"
BRASIL_URL = "https://marxismo.org.br/artigos/brasil/"

def criar_pasta(pasta):
    """Cria a pasta se ela não existir."""
    if not os.path.exists(pasta):
        os.makedirs(pasta)

def buscar_noticias(num_resultados=1020, max_paginas=102):
    """Busca automaticamente notícias da seção Brasil percorrendo várias páginas."""
    print(f"🔍 Buscando até {num_resultados} notícias mais recentes na seção Brasil...")

    links_encontrados = set()  
    pagina = 1

    while len(links_encontrados) < num_resultados and pagina <= max_paginas:
        url_pagina = f"{BRASIL_URL}page/{pagina}/" if pagina > 1 else BRASIL_URL
        print(f"🔄 Rastreando: {url_pagina}...")

        try:
            response = requests.get(url_pagina, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar página {pagina}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        artigos = soup.find_all("article")

        for artigo in artigos:
            link = artigo.find("a")  
            if link and link.get("href").startswith(BASE_URL):
                links_encontrados.add(link["href"])  

        print(f"🔗 {len(links_encontrados)} artigos encontrados até agora.")

     
        if len(links_encontrados) >= num_resultados:
            break

        pagina += 1  

    return list(links_encontrados)[:num_resultados]  

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

def salvar_em_txt_individual(noticias):
    """Salva cada notícia em um arquivo de texto individual dentro da pasta 'noticias-brasil'."""
    pasta = "../noticias"
    criar_pasta(pasta)

    for idx, noticia in enumerate(noticias, 1):
        if not noticia:
            continue  # Pula se a notícia não foi extraída corretamente

        conteudo_noticia = noticia['conteudo']
        num_palavras = len(conteudo_noticia.split())

        if num_palavras >= 200:
            nome_arquivo = f"noticia_brasil_{idx}_{noticia['titulo'].replace(' ', '_').replace('/', '-')}.txt"
            caminho_arquivo = os.path.join(pasta, nome_arquivo)

            with open(caminho_arquivo, "w", encoding="utf-8") as file:
                file.write(f"📰 Notícia: {noticia['titulo']}\n")
                file.write("=" * 80 + "\n\n")
                file.write(f"📅 Data: {noticia['data']}\n")
                file.write(f"🔗 Link: {noticia['url']}\n\n")
                file.write(f"{noticia['conteudo']}\n")
                file.write("=" * 80 + "\n\n")
                time.sleep(2)

            print(f"\n✅ Arquivo salvo como: {caminho_arquivo}")
        else:
            print(f"⚠️ A notícia '{noticia['titulo']}' não tem 200 palavras e foi ignorada.")

if __name__ == "__main__":
    num_noticias = 20  
    max_paginas = 5 

    links_noticias = buscar_noticias(num_resultados=num_noticias, max_paginas=max_paginas)

    noticias_extraidas = []
    for link in links_noticias:
        print(f"📄 Extraindo: {link}")
        noticia = extrair_noticia(link)
        if noticia:
            noticias_extraidas.append(noticia)

    salvar_em_txt_individual(noticias_extraidas)

    print("\n✅ Script finalizado com sucesso!")
