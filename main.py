import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from instabot import Bot
import shutil
from utils.transcricao import openai_whisper_transcrever
from utils.resumo import openai_gpt_resumir_texto
from utils.gerar_imagem import openai_dalle_gerar_imagem, selecionar_imagem, ferramenta_converter_png_para_jpg
from utils.instagram import postar_instagram, confirmacao_postagem, ferramenta_conversao_binario_para_string


def main():
    """Executa todo o fluxo de transcrição, resumo e geração de imagem."""
    load_dotenv()
    caminho_audio = "podcasts/operacaoprato.mp3"
    nome_arquivo = "operacaoprato"
    api_openai = os.getenv("API_KEY_OPENAI")
    client = OpenAI(api_key=api_openai)
    usuario_instagram = os.getenv("USER_INSTAGRAM")
    senha_instagram = os.getenv("PASSWORD_INSTAGRAM")

    transcricao = openai_whisper_transcrever(caminho_audio, nome_arquivo, "whisper-1", client)
    resumo = openai_gpt_resumir_texto(transcricao, nome_arquivo, client)
    # openai_dalle_gerar_imagem(resumo, nome_arquivo, client, 1)
    lista_imagens_geradas = openai_dalle_gerar_imagem(resumo, nome_arquivo, client, 1)

    caminho_imagem_escolhida = selecionar_imagem(lista_imagens_geradas)
    caminho_imagem_convertida = ferramenta_converter_png_para_jpg(caminho_imagem_escolhida, nome_arquivo)
    print(f"Imagem selecionada: {caminho_imagem_escolhida}")
    print(f"Imagem convertida para JPG: {caminho_imagem_convertida}")
    print(f"Usuário: {os.getenv('USER_INSTAGRAM')}")
    print(f"Senha: {os.getenv('PASSWORD_INSTAGRAM')}")
    
    if confirmacao_postagem(caminho_imagem_convertida, ferramenta_conversao_binario_para_string(resumo)).lower() == "s":
        print("Postando no Instagram...")
        postar_instagram(caminho_imagem_convertida, f"{ferramenta_conversao_binario_para_string(resumo)}", usuario_instagram, senha_instagram)


if __name__ == "__main__":
    main()
