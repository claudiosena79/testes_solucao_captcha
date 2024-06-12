import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



# Configuração do navegador
servico = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')  
navegador = webdriver.Chrome(service=servico, options=options)

# URL da página com o CAPTCHA
link = 'https://seeu.pje.jus.br/seeu/processo/consultaPublica.do?actionType=iniciar'


navegador.get(link)

time.sleep(3)

# Encontrar e clicar no botão do CAPTCHA (se necessário)
try:
    navegador.find_element(By.XPATH, '//*[@id="amzn-captcha-verify-button"]').click()
    time.sleep(2)
except:
    print("Botão do CAPTCHA não encontrado ou já clicado.")

# Obter os cookies da sessão do navegador
cookies = navegador.get_cookies()
dicionario_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

# Fazer uma requisição com os cookies para capturar os headers
response = requests.get(link, cookies=dicionario_cookies)
headers = response.headers

# Obter o ID do CAPTCHA
chave_captcha = get_captcha_id(headers)

# Configurar e resolver o CAPTCHA usando AntiCaptcha
solver = recaptchaV3Proxyless()
solver.set_verbose(1)
solver.set_key('ec4da9dfe5fcd7111b837453a808a98c')  # Chave da API do AntiCaptcha
solver.set_website_url(link)
solver.set_website_key(chave_captcha)

resposta = solver.solve_and_return_solution()

if resposta != 0:
    print(resposta)
else:
    print(solver.err_string)

# Manter o navegador aberto por um tempo para inspeção, se necessário
time.sleep(20)
