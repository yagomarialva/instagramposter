from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import time
import os

# Configurações do usuário
LINKEDIN_EMAIL = "yago.marialva@gmail.com"
LINKEDIN_SENHA = "bpeinngcsl"
PALAVRAS_CHAVE = "react"
LOCALIZACAO = "Brasil"
CURRICULO_PATH = os.path.abspath("arquivos/curriculo.pdf")

# Configuração do WebDriver para Firefox
options = webdriver.FirefoxOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # Comente esta linha para visualizar o navegador

# Inicializa o GeckoDriver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

try:
    # Acessa a página de login do LinkedIn
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))

    # Faz login
    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_SENHA)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Aguarda login ser processado
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "global-nav-search")))

    # Pesquisa vagas
    driver.get(f"https://www.linkedin.com/jobs/search/?keywords={PALAVRAS_CHAVE}&location={LOCALIZACAO}")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-container--clickable")))

    # Clica no filtro "Candidatura simplificada"
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Filtro Candidatura simplificada.']"))
        ).click()
        time.sleep(3)
    except Exception as e:
        print("Erro ao aplicar filtro de Candidatura Simplificada:", e)

    # Pega as vagas na lista
    vagas = driver.find_elements(By.CLASS_NAME, "job-card-container--clickable")

    for vaga in vagas[:5]:  # Limita a 5 candidaturas por execução
        try:
            vaga.click()
            time.sleep(3)

            # Verifica se a vaga tem o texto "Candidatura simplificada"
            try:
                # Procura pelo span com o texto "Candidatura simplificada"
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Candidatura simplificada')]"))
                )
            except Exception as e:
                print("Vaga sem candidatura simplificada, ignorando...")
                continue  # Pula para a próxima vaga

            # Clica no botão "Candidatura simplificada"
            botao_candidatar = driver.find_element(By.XPATH, "//span[contains(text(), 'Candidatura simplificada')]")
            botao_candidatar.click()
            time.sleep(2)

            # Preenche perguntas rápidas se existirem
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.get_attribute("type") in ["text", "number"]:
                    input_field.send_keys("Sim")  # Responde automaticamente "Sim" em perguntas simples

            # Anexa o currículo
            upload_field = driver.find_element(By.XPATH, "//input[@type='file']")
            upload_field.send_keys(CURRICULO_PATH)
            time.sleep(2)

            # Enviar candidatura
            driver.find_element(By.XPATH, "//button[contains(text(),'Enviar candidatura')]").click()
            time.sleep(3)

        except Exception as e:
            print(f"Erro ao se candidatar: {e}")
            continue

    print("Candidaturas concluídas!")

finally:
    driver.quit()
