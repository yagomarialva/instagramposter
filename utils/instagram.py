import os
import shutil
from instabot import Bot

def ferramenta_conversao_binario_para_string(texto):
    if isinstance(texto, bytes):
        return str(texto.decode())
    return texto

def postar_instagram(caminho_imagem, texto, user, password):
    """Posta uma imagem com legenda no Instagram."""
    if os.path.exists("config"):
        shutil.rmtree("config")
    
    bot = Bot()
    bot.login(username=user, password=password)
    
    legenda_cortada = texto[:2200]  # Limita a legenda para evitar erro do Instagram
    bot.upload_photo(caminho_imagem, caption=legenda_cortada)

def confirmacao_postagem(caminho_imagem_convertida, legenda_postagem):
    """Confirma se o usuário deseja postar no Instagram."""
    print(f"\nCaminho da Imagem: {caminho_imagem_convertida}") 
    print(f"Legenda: {legenda_postagem}") 
    
    return input("\nDeseja postar no Instagram? Digite 's' para sim e 'n' para não: ").strip().lower()
