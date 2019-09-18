import requests
import urllib.request
from bs4 import BeautifulSoup
import os.path
import unicodedata
import re
import json

domain = 'https://autos.mercadolibre.com.ar/'
headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/50.0.2661.102 Safari/537.36'}

# funcion para normalizar los datos (filtros) que se van obteniendo, elimnar espacios, acentos, etc


def normalizar(list):
    for i in range(0, len(list)):
        list[i] = unicodedata.normalize('NFD', list[i]) \
            .encode('ascii', 'ignore') \
            .decode("utf-8")
        list[i] = list[i][1:-1]
        list[i] = re.sub(r'\([^)]*\)', '', list[i])
        list[i] = list[i][:-1]


def downloadLinks ():
    response = requests.get(domain, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    path = './download/ml/'

    if not os.path.exists(path):
        os.makedirs(path)

    links = {}

    y = 0

    brands = []

    # voy a filtrar primero por marcas, asi que comienzo a obteniendo las marcas

    for a_tag in soup.findAll('dl', {'id': 'id_9991744-AMLA_1744_1'}):
        for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
            brands += [b.text.lower().replace(' ', '-')]

    normalizar(brands)

    marcas = []

    for i in brands:
        if i not in marcas:
            marcas.append(i)

    # armo los links con los filtros de las marcas

    linksM = []

    for i in range(0, len(marcas)):
            linksM += ['https://autos.mercadolibre.com.ar/' + str(marcas[i]) + '/']

    # ahora voy a filtrar por los modelos de cada marca asi que los obtengo

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

        # armo los links con los filtros de marca y modelo

        linksMM = []

        for i in range(0, len(modelos)):
            linksMM += [linksM[u] + str(modelos[i]) + '/']

        # ahora filtro por ciudad

        for k in range(0, len(linksMM)):
            url_bm = linksMM[k]
            response = requests.get(url_bm, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            places = []

            for a_tag in soup.findAll('dl', {'id': 'id_state'}):
                for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
                    places += [b.text.lower().replace('.', '').replace(' ', '-')]

            normalizar(places)

            # ahora añado el filtro de ciudad

            lugares = []

            for i in places:
                if i not in lugares:
                    lugares.append(i)

            for i in range(0, len(lugares)):
                if lugares[i] == 'cordoba':
                    lugares[i] = '_PciaId_cordoba'
                if lugares[i] == 'santa-fe':
                    lugares[i] = '_PciaId_santa-fe'

            # armo los links con los filtros de marca, modelo y ciudad

            linksMML = []

            for i in range(0, len(lugares)):
                if str(lugares[i]) == '_PciaId_cordoba' or str(lugares[i]) == '_PciaId_santa-fe':
                    linksMML += [linksMM[k] + str(lugares[i])]
                else:
                    linksMML += [linksMM[k] + str(lugares[i]) + '/']

            # ahora obtengo el numero de resultados por pagina para luego armar los links

            for j in range(0, len(linksMML)):
                url_bmp = linksMML[j]
                response = requests.get(url_bmp, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                tag2 = soup.findAll('div', {'class': 'quantity-results'})
                tag2 = str(tag2)
                tag2 = tag2.replace('.', '')

                lista = re.findall('\d+', tag2)

                num = int(lista[0])

                # armo los links de las paginas

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
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")

                    # obtengo los links de las publaciones que hay por cada pagina

                    links_pubs = []

                    for i in range(109, len(soup.findAll('a'))):
                        tag = soup.findAll('a')[i]
                        href = tag['href']
                        if '/MLA-' in href and '[BB:' not in href:
                            links_pubs += [href]

                    links_per_page = []

                    for i in links_pubs:
                        if i not in links_per_page:
                            links_per_page.append(i)

                    for i in range(0, len(links_per_page)):
                        links['url' + str(y)] = links_per_page[i]
                        with open(path + "item_links.json", "w") as file:
                            json.dump(links, file)
                        print("Saved", links['url' + str(y)], "saved links number:", y)
                        y += 1


path = './download/ml/item_links.json'

if not os.path.exists(path):
    downloadLinks()
else:
    with open('./download/ml/item_links.json', 'r') as f:
        dominios = f.read()

    doms = json.loads(dominios)

    count = 0

    while count <= 100:   ########################################## aca tendria que ir el numero de links que hay en el json
        url_public = doms['url' + str(count)]
        print(url_public, count)

        response = requests.get(url_public, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # obtengo el ID de la publicacion en la que me encuentro

        url_public_str = str(url_public)
        ides = re.findall('\d+', url_public_str)
        ides = list(map(int, ides))
        ID = max(ides)

        # obtengo los datos del vehiculo

        datos_vehiculo = {}
        campos = []

        for li_tag in soup.findAll('ul', {'class': 'specs-list'}):
            for span_tag in li_tag.find_all('li'):
                value = span_tag.find('span').text
                field = span_tag.find('strong').text
                campos += [field]
                if value != '':
                    datos_vehiculo[field] = value

        # obtengo la marca y modelo del vehiculo

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

        with open('./download/ml/' + str(marca).lower().replace(' ', '-') + '/' + str(ID) + '/meta.json', 'w') as fp:
            json.dump(datos_vehiculo, fp)

        print("Creado meta.json")

        # obtengo los links de las imagenes de la publicacion en la que me encuentro

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
                print("Descargada la imagen", y + 1, "/", str(marca), str(modelo), "/",  place)
            except Exception as e:
                print(str(e), imagenes[y])

            y = y + 1

        count = count + 1

print("End")
