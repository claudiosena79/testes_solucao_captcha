import os
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

#Cria uma sessão para reutilizar a mesma conexão em várias solicitações
client = requests.Session()

#Capsolver API
CAPSOLVER_API_KEY = "CAP-F24C480FD9FDDCFE8CDB06DB02B25863"
CAPSOLVER_API_ENDPOINT = "https://api.capsolver.com/createTask"

# URL da página com o CAPTCHA
link = 'https://seeu.pje.jus.br/seeu/processo/consultaPublica.do?actionType=iniciar'

# Extrair dados (iv, key e contest) do conteudo do script
script_content = client.get(link).text
#Match objects
key_match = re.search(r'"key":"([^"]+)"', script_content)
iv_match = re.search(r'"iv":"([^"]+)"', script_content)
context_match = re.search(r'"context":"([^"]+)"', script_content)
jschallange_match = re.search(r'<script.*?src="(.*?)".*?></script>', script_content)

#Extraindo os dados dos match objects
if key_match and iv_match and context_match:
  key = key_match.group(1)
  iv = iv_match.group(1)
  context = context_match.group(1)
  jschallange = jschallange_match.group(1)
else:
  print("Key, IV, or Context not found in the script.")


#preparar dados da requisição POST para solicitar resolução de captcha
dados = {
    "clientKey": CAPSOLVER_API_KEY,
    "task": {
        "type": "AntiAwsWafTaskProxyLess",
        "websiteURL": link,
        "awsKey": key,
        "awsIv": iv,
        "awsContext": context,
        "awsChallengeJS": jschallange
    }
}
print(dados)
#Enviar requisição POST para CAPSOLVER API para criar tarefa e receber o id da tarefa
task_id_response = client.post(CAPSOLVER_API_ENDPOINT, json=dados)
task_id = task_id_response.json()['taskId']

time.sleep(10)

# Envie uma requisição POST para obter a solução da tarefa do  CAPTCHA usando o id da tarefa
cookie_response = client.post("https://api.capsolver.com/getTaskResult", json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}).json()

if cookie_response["status"] == "ready":
  # Obtenha o cookie (AWS WAF token)
  cookie = cookie_response["solution"]["cookie"]
  
  #Faça uma requisição GET passando o AWS WAF token obtido  como cookie
  website_content = client.get(link, cookies={"aws-waf-token": cookie})
  
  # Print the content of the protected website
  print(website_content.text)
  response = requests.get(link)

  print(response.status_code) #output = 405
  print(response.text)

  servico = Service(ChromeDriverManager().install())
  options = Options()
  options.add_argument('--enable-javascript')
  options.add_argument('--disable-blink-features=AutomationControlled')
  options.add_argument('--disable-extensions')
  options.add_argument('--disable-gpu')
  options.add_argument('--no-sandbox')
  options.add_argument('--headless')  # Executar em modo headless se necessário
  navegador = webdriver.Chrome(service=servico, options=options)
  # Print the content of the protected website
  html_content = website_content.text

  with open('resultado.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

#Abrir o arquivo HTML no navegador
  navegador.get("http://localhost:8000/resultado.html")

  time.sleep(30)

else:
  print("capsolver failed to solve the captcha, please try again. ")


