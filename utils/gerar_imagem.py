import os
import requests
from PIL import Image

def openai_dalle_gerar_imagem(resumo_para_imagem, nome_arquivo, client, quantidade=1):
    """Gera imagens com base no resumo da notícia."""
    caminhos_imagens = [f"imagens/{nome_arquivo}_{i}.png" for i in range(quantidade)]

    if all(os.path.exists(img) for img in caminhos_imagens):
        print("Imagens já existem. Pulando geração...")
        return caminhos_imagens

    print("Gerando imagens com DALL-E...")
    resumo_truncado = resumo_para_imagem[:1000]  # Limita o texto para evitar erro na API

    prompt_user = f"Uma pintura futurista e misteriosa, sem texto, 3D que retrate: {resumo_truncado}."

    imagens_geradas = [
        client.images.generate(
            model="dall-e-3",
            prompt=prompt_user,
            n=1,
            size="1024x1024"
        ).data[0].url
        for _ in range(quantidade)
    ]

    for i, url in enumerate(imagens_geradas):
        imagem = requests.get(url)
        with open(caminhos_imagens[i], "wb") as arquivo:
            arquivo.write(imagem.content)

    return caminhos_imagens

def selecionar_imagem(lista_nome_imagens):
    """Permite que a pessoa usuária selecione uma imagem da lista gerada."""
    print("Imagens geradas:")
    for i, nome_imagem in enumerate(lista_nome_imagens):
        print(f"{i}: {nome_imagem}")

    escolha = int(input("Qual imagem você deseja selecionar? Informe o número da imagem gerada: "))
    return lista_nome_imagens[escolha]

def ferramenta_converter_png_para_jpg(caminho_imagem_escolhida, nome_arquivo):
    """Converte uma imagem PNG para JPG."""
    img_png = Image.open(caminho_imagem_escolhida)
    caminho_jpg = caminho_imagem_escolhida.replace(".png", ".jpg")
    img_png.save(caminho_jpg, "JPEG")
    return caminho_jpg
