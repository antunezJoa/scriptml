import requests
import urllib.request
from bs4 import BeautifulSoup
import os.path
import unicodedata
import re
import json
import time

domain = 'https://autos.mercadolibre.com.ar/'
headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/50.0.2661.102 Safari/537.36'}

path = './download/ml/'

if not os.path.exists(path):
    os.makedirs(path)

response = requests.get(domain, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

'''funcion para normalizar los datos que se van obteniendo, elimnar espacios, acentos, etc'''

def normalizar(list):
    for i in range(0, len(list)):
        list[i] = unicodedata.normalize('NFD', list[i]) \
            .encode('ascii', 'ignore') \
            .decode("utf-8")
        list[i] = list[i][1:-1]
        list[i] = re.sub(r'\([^)]*\)', '', list[i])
        list[i] = list[i][:-1]

brands = []

'''voy a filtrar primero por marcas, asi que comienzo a obteniendo las marcas'''

for a_tag in soup.findAll('dl', {'id': 'id_9991744-AMLA_1744_1'}):
    for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
        brands += [b.text.lower().replace(' ', '-')]

normalizar(brands)

marcas = []

for i in brands:
    if i not in marcas:
        marcas.append(i)

'''armo los links con los filtros de las marcas'''

linksM = []

for i in range(0, len(marcas)):
        linksM += ['https://autos.mercadolibre.com.ar/' + str(marcas[i]) + '/']

'''ahora voy a filtrar por los modelos de cada marca asi que los obtengo'''

for u in range(0, len(linksM)):
    url_b = linksM[u]
    response = requests.get(url_b, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    models = []

    for a_tag in soup.findAll('dl', {'id': 'id_9991744-AMLA_1744_2'}):
        for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
            models += [b.text.lower().replace(' ', '-').replace('!', '')]

    normalizar(models)

    modelos = []

    for i in models:
        if i not in modelos:
            modelos.append(i)

    '''armo los links con los filtros de marca y modelo'''

    linksMM = []

    for i in range(0, len(modelos)):
        linksMM += [linksM[u] + str(modelos[i]) + '/']

    '''ahora filtro por ciudad'''

    for k in range(0, len(linksMM)):
        url_bm = linksMM[k]
        response = requests.get(url_bm, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        places = []

        for a_tag in soup.findAll('dl', {'id': 'id_state'}):
            for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
                places += [b.text.lower().replace('.', '').replace(' ', '-')]

        normalizar(places)

        '''ahora añado el filtro de ciudad'''

        lugares = []

        for i in places:
            if i not in lugares:
                lugares.append(i)

        for i in range(0, len(lugares)):
            if lugares[i] == 'cordoba':
                lugares[i] = '_PciaId_cordoba'
            if lugares[i] == 'santa-fe':
                lugares[i] = '_PciaId_santa-fe'

        '''armo los links con los filtros de marca, modelo y ciudad'''

        linksMML = []

        for i in range(0, len(lugares)):
            if str(lugares[i]) == '_PciaId_cordoba' or str(lugares[i]) == '_PciaId_santa-fe':
                linksMML += [linksMM[k] + str(lugares[i])]
            else:
                linksMML += [linksMM[k] + str(lugares[i]) + '/']

        '''ahora obtengo el numero de resultados por pagina para luego armar los links'''

        for j in range(0, len(linksMML)):
            url_bmp = linksMML[j]
            response = requests.get(url_bmp, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            tag2 = soup.findAll('div', {'class': 'quantity-results'})
            tag2 = str(tag2)
            tag2 = tag2.replace('.', '')

            lista = re.findall('\d+', tag2)

            num = int(lista[0])

            '''armo los links de las paginas'''

            if num <= 48:
                links_paginas = [url_bmp]
            else:
                k = 49
                links_paginas = [url_bmp]
                while k <= num:
                    if '_PciaId_cordoba' in url_bmp or '_PciaId_santa-fe' in url_bmp:
                        links_paginas += [url_bmp + '/_Desde_' + str(k)]
                        k = k + 48
                    else:
                        links_paginas += [url_bmp + '_Desde_' + str(k)]
                        k = k + 48

            for r in range(0, len(links_paginas)):
                url = links_paginas[r]
                #print(url)
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                '''obtengo los links de las publaciones que hay por cada pagina'''

                links_pubs = []

                for i in range(109, len(soup.findAll('a'))):
                    tag = soup.findAll('a')[i]
                    href = tag['href']
                    if '/MLA-' in href and '[BB:1]' not in href:
                        links_pubs += [href]

                links_per_page = []

                for i in links_pubs:
                    if i not in links_per_page:
                        links_per_page.append(i)

                for z in range(0, len(links_per_page)):
                    
