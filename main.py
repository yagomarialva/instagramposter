import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import random
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

def gerar_audio_ia(texto, nome_arquivo, client):
    """Gera um áudio do texto usando a IA da OpenAI."""
    print("🎙️ Gerando áudio do resumo...")
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "alloy", "format": "wav"},
            messages=[{"role": "user", "content": texto}]
        )

        # Decodificar o áudio gerado
        wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)

        # Criar pasta para armazenar os áudios
        pasta_audios = "audios"
        os.makedirs(pasta_audios, exist_ok=True)

        caminho_audio = os.path.join(pasta_audios, f"{nome_arquivo}.wav")

        with open(caminho_audio, "wb") as f:
            f.write(wav_bytes)

        print(f"✅ Áudio gerado e salvo em: {caminho_audio}")
        return caminho_audio
    except Exception as e:
        print(f"❌ Erro ao gerar áudio: {e}")
        return None

def main():
    """Executa o fluxo de transcrição, resumo, leitura em voz e geração de imagem."""
    load_dotenv()
    nome_arquivo = "noticias/noticia_brasil_1_PT_e_PSOL_se_unem_a_bolsonaristas_na_Alerj_e_Câmara_do_Rio_de_Janeiro"
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

    # Pergunta ao usuário se deseja gerar um áudio do resumo
    gerar_audio = input("🎙️ Deseja gerar um áudio para este resumo? (s/n): ").strip().lower()
    if gerar_audio == "s":
        caminho_audio = gerar_audio_ia(nome_arquivo, nome_arquivo, client)
    else:
        print("🔇 Áudio não gerado.")

    # Pergunta ao usuário se deseja criar uma nova imagem
    gerar_imagem = input("🖼️ Deseja gerar uma nova imagem para esta notícia? (s/n): ").strip().lower()

    if gerar_imagem == "s":
        lista_imagens_geradas = openai_dalle_gerar_imagem(resumo, nome_arquivo, client, 1)
        caminho_imagem_escolhida = selecionar_imagem(lista_imagens_geradas)
        caminho_imagem_convertida = ferramenta_converter_png_para_jpg(caminho_imagem_escolhida, nome_arquivo)
        print(f"🖼️ Imagem gerada e pronta: {caminho_imagem_convertida}")

    else:
        print("🔍 Procurando uma imagem existente na pasta 'imagens/'...")
        imagem_existente = buscar_imagem_existente()

        if imagem_existente:
            caminho_imagem_convertida = ferramenta_converter_png_para_jpg(imagem_existente, nome_arquivo)
            print(f"🖼️ Imagem convertida para JPG: {caminho_imagem_convertida}")
        else:
            print("❌ Nenhuma imagem encontrada na pasta 'imagens/'. Finalizando o processo.")
            return  # Sai do programa se não houver imagem

    # Confirma e posta no Instagram, se houver imagem gerada ou convertida
    if caminho_imagem_convertida and confirmacao_postagem(caminho_imagem_convertida, ferramenta_conversao_binario_para_string(resumo)).lower() == "s":
        print("🚀 Postando no Instagram...")
        postar_instagram(caminho_imagem_convertida, ferramenta_conversao_binario_para_string(resumo), usuario_instagram, senha_instagram)
    else:
        print("✅ Processo finalizado sem postagem no Instagram.")

if __name__ == "__main__":
    main()
