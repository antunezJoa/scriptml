import requests
import urllib.request
import unicodedata
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

all_links = []
brands = []

for a_tag in soup.findAll('dl', {'id': 'id_9991744-AMLA_1744_1'}):
    for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
        brands += [b.text.lower().replace(' ', '-')]

for i in range(0, len(brands)):
    brands[i] = unicodedata.normalize('NFD', brands[i]) \
        .encode('ascii', 'ignore') \
        .decode("utf-8")
    brands[i] = brands[i][1:-1]

for i in range(0, len(brands)):
    brands[i] = re.sub(r'\([^)]*\)', '', brands[i])
    brands[i] = brands[i][:-1]

marcas = []

for i in brands:
    if i not in marcas:
        marcas.append(i)

linksM = []

for i in range(0, len(marcas)):
        linksM += ['https://autos.mercadolibre.com.ar/' + str(marcas[i]) + '/']

u = 0

for u in range(0, len(linksM)):
    url_b = linksM[u]
    response = requests.get(url_b, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    models = []

    for a_tag in soup.findAll('dl', {'id': 'id_9991744-AMLA_1744_2'}):
        for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
            models += [b.text.lower().replace(' ', '-').replace('!', '')]

    for i in range(0, len(models)):
        models[i] = unicodedata.normalize('NFD', models[i]) \
            .encode('ascii', 'ignore') \
            .decode("utf-8")
        models[i] = models[i][1:-1]

    for i in range(0, len(models)):
        models[i] = re.sub(r'\([^)]*\)', '', models[i])
        models[i] = models[i][:-1]

    modelos = []

    for i in models:
        if i not in modelos:
            modelos.append(i)

    linksMM = []

    for i in range(0, len(modelos)):
        linksMM += [linksM[u] + str(modelos[i]) + '/']

    for k in range(0, len(linksMM)):
        url_bm = linksMM[k]
        response = requests.get(url_bm, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        places = []

        for a_tag in soup.findAll('dl', {'id': 'id_state'}):
            for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
                places += [b.text.lower().replace('.', '').replace(' ', '-')]

        for i in range(0, len(places)):
            places[i] = unicodedata.normalize('NFD', places[i]) \
                .encode('ascii', 'ignore') \
                .decode("utf-8")
            places[i] = places[i][1:-1]

        for i in range(0, len(places)):
            places[i] = re.sub(r'\([^)]*\)', '', places[i])
            places[i] = places[i][:-1]

        lugares = []

        for i in places:
            if i not in lugares:
                lugares.append(i)

        for i in range(0, len(lugares)):
            if lugares[i] == 'cordoba':
                lugares[i] = '_PciaId_cordoba'
            if lugares[i] == 'santa-fe':
                lugares[i] = '_PciaId_santa-fe'

        linksMML = []

        for i in range(0, len(lugares)):
            linksMML += [linksMM[k] + str(lugares[i])]

        j = 0

        for j in range(0, len(linksMML)):
            url_bmp = linksMML[j]
            response = requests.get(url_bmp, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            tag2 = soup.findAll('div', {'class': 'quantity-results'})
            tag2 = str(tag2)
            tag2 = tag2.replace('.', '')

            lista = re.findall('\d+', tag2)

            num = int(lista[0])

            if num <= 48:
                links_paginas = [url_bmp]
            else:
                k = 49
                links_paginas = [url_bmp]
                while k <= num:
                    links_paginas += [url_bmp + '/_Desde_' + str(k)]
                    k = k + 48

            for r in range(0, len(links_paginas)):
                url = links_paginas[r]
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                '''obtengo los links de las publaciones que hay por cada pagina'''

                links_pubs = []

                for i in range(116, len(soup.findAll('a'))):
                    tag = soup.findAll('a')[i]
                    href = tag['href']
                    if '/MLA-' in href:
                        links_pubs += [href]

                links_per_page = []

                for i in links_pubs:
                    if i not in links_per_page:
                        links_per_page.append(i)

                '''for para recorrer todas las publicaciones dentro de una pagina'''

                z = 0

                for z in range(0, len(links_per_page)):
                    url_public = links_per_page[z]
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

                    datos = []

                    for i in range(0, len(soup.findAll('a', {'class': 'breadcrumb'}))):
                        tag = soup.findAll('a', {'class': 'breadcrumb'})[i].text.replace('\t', '').replace('\n', '')
                        datos += [tag]

                    datos_vehiculo['Marca'] = datos[2]
                    datos_vehiculo['Modelo'] = datos[3]
                    marca = datos[2]
                    modelo = datos[3]

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

                    i = 0
                    place = []

                    for div_tag in soup.findAll('div', {'class': 'location-info'}):
                        place = div_tag.find('span').text
                        i = i + 1
                        if i > 0:
                            break

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
                            print("Descargada la imagen", y + 1, "de la publicacion", z + 1, "de la pagina", r + 1, "/", place, "/", str(marca), str(modelo))
                        except Exception as e:
                            print(str(e), imagenes[y])

                        y = y + 1

print("End")
