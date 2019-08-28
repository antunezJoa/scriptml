import requests
import urllib.request
from bs4 import BeautifulSoup
import os.path
import re
import json

domain = 'https://autos.mercadolibre.com.ar/'
headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/50.0.2661.102 Safari/537.36'}

response = requests.get(domain, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

cant_res = soup.find('div',attrs={'class':'quantity-results'}).text
cant_res = str(cant_res)
cant_res = cant_res.replace('.', '')
cant_res = cant_res.split(' ',2)
num_pubs = int(cant_res[1])

k = 97
links_paginas = ['https://autos.mercadolibre.com.ar/', 'https://autos.mercadolibre.com.ar/_Desde_49']

while k <= num_pubs:
    links_paginas += ['https://autos.mercadolibre.com.ar/_Desde_' + str(k)]
    k = k + 48

print(links_paginas)
