import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.transcricao import openai_whisper_transcrever
from utils.resumo import openai_gpt_resumir_texto
from utils.gerar_imagem import openai_dalle_gerar_imagem, selecionar_imagem, ferramenta_converter_png_para_jpg
from utils.instagram import postar_instagram, confirmacao_postagem, ferramenta_conversao_binario_para_string

def obter_caminho_arquivo(nome_arquivo):
    """Verifica se o áudio existe, senão busca o texto na pasta de notícias."""
    caminho_audio = os.path.join("podcasts", f"{nome_arquivo}.mp3")
    caminho_texto = os.path.join("noticias", f"{nome_arquivo}.txt")

    if os.path.exists(caminho_audio):
        return "audio", caminho_audio  # Processa via transcrição
    elif os.path.exists(caminho_texto):
        return "texto", caminho_texto  # Processa direto via texto
    else:
        print(f"❌ Nenhum arquivo encontrado para {nome_arquivo}.")
        return None, None

def main():
    """Executa o fluxo de transcrição, resumo e geração de imagem."""
    load_dotenv()
    nome_arquivo = "noticia_31_Congresso_dos_EUA_e_OVNIs:_o_que_foi_revelado_na_segunda_audiência_sobre_UFOs"
    api_openai = os.getenv("API_KEY_OPENAI")
    client = OpenAI(api_key=api_openai)
    usuario_instagram = os.getenv("USER_INSTAGRAM")
    senha_instagram = os.getenv("PASSWORD_INSTAGRAM")

    # Verifica onde está o conteúdo
    tipo_arquivo, caminho_arquivo = obter_caminho_arquivo(nome_arquivo)
    if not caminho_arquivo:
        return

    if tipo_arquivo == "audio":
        print("🎙️ Processando áudio...")
        transcricao = openai_whisper_transcrever(caminho_arquivo, nome_arquivo, "whisper-1", client)
        pasta_destino = "transcricoes"
    else:
        print("📄 Processando texto...")
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            transcricao = file.read()
        pasta_destino = "noticias"

    # Gera resumo
    resumo = openai_gpt_resumir_texto(transcricao, nome_arquivo, client)

    # Salva o resumo no diretório correto
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_resumo = os.path.join(pasta_destino, f"{nome_arquivo}_resumo.txt")
    with open(caminho_resumo, "w", encoding="utf-8") as file:
        file.write(resumo)

    print(f"✅ Resumo salvo em: {caminho_resumo}")

    # Gera imagem
    lista_imagens_geradas = openai_dalle_gerar_imagem(resumo, nome_arquivo, client, 1)
    caminho_imagem_escolhida = selecionar_imagem(lista_imagens_geradas)
    caminho_imagem_convertida = ferramenta_converter_png_para_jpg(caminho_imagem_escolhida, nome_arquivo)

    print(f"🖼️ Imagem pronta: {caminho_imagem_convertida}")

    # Confirma e posta no Instagram
    if confirmacao_postagem(caminho_imagem_convertida, ferramenta_conversao_binario_para_string(resumo)).lower() == "s":
        print("🚀 Postando no Instagram...")
        postar_instagram(caminho_imagem_convertida, ferramenta_conversao_binario_para_string(resumo), usuario_instagram, senha_instagram)

if __name__ == "__main__":
    main()
