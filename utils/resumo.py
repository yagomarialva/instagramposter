import os

def ferramenta_ler_arquivo(caminho_arquivo):
    """Lê o conteúdo de um arquivo de texto se ele existir."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        return None

def ferramenta_salvar_arquivo(caminho_arquivo, conteudo):
    """Salva conteúdo em um arquivo de texto."""
    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)

def openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, client):
    """Gera um resumo da transcrição para um post no Instagram."""
    caminho_resumo_txt = f"resumos_instagram/resumo_instagram_{nome_arquivo}.txt"

    if resumo := ferramenta_ler_arquivo(caminho_resumo_txt):
        print("Resumo já existe. Pulando a geração...")
        return resumo

    print("Resumindo com o GPT...")
    prompt_sistema = """
    Assuma que você é um digital influencer criando conteúdos.
    - Seja criativo e autêntico.
    - Use linguagem formal.
    - Faça um resumo envolvente com no máximo 1000 caracteres.
    - Inclua hashtags relevantes.
    - Inclua emogis para chamar atenção.
    - Não copie e cole o texto original.
    - Não faça chamada de podcast.
    """

    resposta = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": transcricao_completa}
        ],
        temperature=0.6
    )

    resumo_instagram = resposta.choices[0].message.content.strip()
    ferramenta_salvar_arquivo(caminho_resumo_txt, resumo_instagram)
    return resumo_instagram
