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

'''
cant_res = soup.find('div', attrs={'class': 'quantity-results'}).text
cant_res = str(cant_res)
cant_res = cant_res.replace('.', '')
cant_res = cant_res.split(' ', 2)
num_pubs = int(cant_res[1])
'''

'''while para crear el array con los links de todas las páginas'''

k = 97
links_paginas = ['https://autos.mercadolibre.com.ar/', 'https://autos.mercadolibre.com.ar/_Desde_49']

while k <= 1969:
    links_paginas += ['https://autos.mercadolibre.com.ar/_Desde_' + str(k)]
    k = k + 48

'''for para recorrer todas las paginas de autos'''

j = 0

for j in range(0, len(links_paginas)):
    url = links_paginas[j]
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    '''obtengo los links de las publaciones que hay por cada pagina'''

    links_pubs = []

    for i in range(892, len(soup.findAll('a'))):
        tag = soup.findAll('a')[i]
        href = tag['href']
        if '/MLA-' in href:
            links_pubs += [href]

    links_per_page = []

    for i in links_pubs:
        if i not in links_per_page:
            links_per_page.append(i)

    '''for para recorrer todas las publicaciones dentro de una pagina'''

    u = 0

    for u in range(0, len(links_per_page)):
        url_public = links_per_page[u]
        print(url_public)
        response = requests.get(url_public, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        '''obtengo el ID de la publicacion en la que me encuentro'''

        url_public_str = str(url_public)
        ides = re.findall('\d+', url_public_str)
        ides = list(map(int, ides))
        ID = max(ides)

        '''obtengo los datos del vehiculo'''

        datos_vehiculo = {}
        campos = []

        for li_tag in soup.findAll('ul', {'class': 'specs-list'}):
            for span_tag in li_tag.find_all('li'):
                value = span_tag.find('span').text
                field = span_tag.find('strong').text
                campos += [field]
                if value != '':
                    datos_vehiculo[field] = value

        '''obtengo la marca y modelo del vehiculo'''

        tag = []

        for i in range(17, 18):
            tag = soup.findAll('p')[i].text.replace(' ', '').split('|', 2)

        datos_vehiculo['Marca'] = tag[0]
        datos_vehiculo['Modelo'] = tag[1]
        marca = tag[0]

        path = './download/ml/' + str(marca).lower().replace(' ', '-') + '/' + str(ID) + '/'

        if not os.path.exists(path):
            os.makedirs(path)

        '''funcion para crear archivos json'''

        def writetojsonfile(path, data):
            filepathnamewext = path + 'meta.json'
            with open(filepathnamewext, 'w') as fp:
                json.dump(data, fp)

        '''creo el archivo .json con las características del vehiculo'''

        writetojsonfile('./download/ml/' + str(marca).lower().replace(' ', '-') + '/' + str(ID) + '/', datos_vehiculo)

        print("Creado meta.json")

        '''obtengo los links de las imagenes de la publicacion en la que me encuentro'''

        q = 0
        imagenes = []

        for i in range(0, len(soup.findAll('img'))):
            tag = soup.findAll('img')[i]
            if tag.get('data-srcset') is not None:
                image = tag.get('data-srcset').replace(' 2x', '').replace('webp', 'jpg')
                imagenes += [image]
                q = q + 1

        y = 0

        while y < q:
            try:
                urllib.request.urlretrieve(imagenes[y], './download/ml/' + str(marca).lower().replace(' ', '-') + '/' + str(ID) + '/' + str(marca).lower() + '_' + str(ID) + '_' + str(y + 1) + '.jpg')
                print("Descargada la imagen", y + 1, "de la publicacion", u + 1, "de la pagina", j + 1)
            except Exception as e:
                print(str(e), imagenes[y])

            y = y + 1

print("End")
