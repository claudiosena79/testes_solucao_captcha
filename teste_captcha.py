import requests
from pprint import pprint

#verificar statuscode e iv, contest e key
WEBSITE_URL = 'https://seeu.pje.jus.br/seeu/processo/consultaPublica.do?actionType=iniciar'
response = requests.get(WEBSITE_URL)

print(response.status_code) #output = 405
pprint(response.text)