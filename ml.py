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


def normalize(list):
    for i in range(0, len(list)):
        list[i] = unicodedata.normalize('NFD', list[i]) \
            .encode('ascii', 'ignore') \
            .decode("utf-8")
        list[i] = list[i][1:-1]
        list[i] = re.sub(r'\([^)]*\)', '', list[i])
        list[i] = list[i][:-1]

# funcion para guardar los links dentro de un .json


def savelinks():
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

    normalize(brands)

    # elimino duplicados

    brands2 = []

    for i in brands:
        if i not in brands2:
            brands2.append(i)

    # armo los links con los filtros de las marcas

    links_b = []

    for i in range(0, len(brands2)):
            links_b += ['https://autos.mercadolibre.com.ar/' + str(brands2[i]) + '/']

    # ahora voy a filtrar por los modelos de cada marca asi que los obtengo

    for u in range(0, len(links_b)):
        url_b = links_b[u]
        response = requests.get(url_b, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        models = []

        for a_tag in soup.findAll('dl', {'id': 'id_9991744-AMLA_1744_2'}):
            for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
                models += [b.text.lower().replace(' ', '-').replace('!', '')]

        normalize(models)

        # elimino duplicados

        models2 = []

        for i in models:
            if i not in models2:
                models2.append(i)

        # armo los links con los filtros de marca y modelo

        links_bm = []

        for i in range(0, len(models2)):
            links_bm += [links_b[u] + str(models2[i]) + '/']

        # ahora filtro por ciudad

        for k in range(0, len(links_bm)):
            url_bm = links_bm[k]
            response = requests.get(url_bm, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            locations = []

            for a_tag in soup.findAll('dl', {'id': 'id_state'}):
                for b in a_tag.findAll('a', {'class': 'qcat-truncate'}):
                    locations += [b.text.lower().replace('.', '').replace(' ', '-')]

            normalize(locations)

            # elimino duplicados

            locations2 = []

            for i in locations:
                if i not in locations2:
                    locations2.append(i)

            for i in range(0, len(locations2)):
                if locations2[i] == 'cordoba':
                    locations2[i] = '_PciaId_cordoba'
                if locations2[i] == 'santa-fe':
                    locations2[i] = '_PciaId_santa-fe'

            # armo los links con los filtros de marca, modelo y ciudad

            links_bml = []

            for i in range(0, len(locations2)):
                if str(locations2[i]) == '_PciaId_cordoba' or str(locations2[i]) == '_PciaId_santa-fe':
                    links_bml += [links_bm[k] + str(locations2[i])]
                else:
                    links_bml += [links_bm[k] + str(locations2[i]) + '/']

            # ahora obtengo el numero de resultados por pagina para luego armar los links

            for j in range(0, len(links_bml)):
                url_bml = links_bml[j]
                print(url_bml)
                response = requests.get(url_bml, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                tag2 = soup.findAll('div', {'class': 'quantity-results'})
                tag2 = str(tag2)
                tag2 = tag2.replace('.', '')

                list_nums = re.findall('\d+', tag2)

                if not list_nums:
                    print("Invalid link")
                    continue
                else:
                    num = int(list_nums[0])

                # armo los links de las paginas

                if num <= 48:
                    links_pages = [url_bml]
                else:
                    k = 49
                    links_pages = [url_bml]
                    while k <= num:
                        if '_PciaId_cordoba' in url_bml:
                            url_bml2 = url_bml.replace('_PciaId_cordoba', '')
                            links_pages += [url_bml2 + '_Desde_' + str(k) + '_PciaId_cordoba']
                            k = k + 48

                        elif '_PciaId_santa-fe' in url_bml:
                            url_bml2 = url_bml.replace('_PciaId_santa-fe', '')
                            links_pages += [url_bml2 + '_Desde_' + str(k) + '_PciaId_santa-fe']
                            k = k + 48

                        else:
                            links_pages += [url_bml + '_Desde_' + str(k)]
                            k = k + 48

                # obtengo los links de las publaciones que hay por cada pagina

                for r in range(0, len(links_pages)):
                    url = links_pages[r]
                    print(url)
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")

                    links_pubs = []

                    for i in range(0, len(soup.findAll('a'))):
                        tag = soup.findAll('a')[i]
                        href = tag['href']
                        if '/MLA-' in href and '[BB:' not in href:
                            links_pubs += [href]

                    # elimino duplicados

                    links_per_page = []

                    for i in links_pubs:
                        if i not in links_per_page:
                            links_per_page.append(i)

                    # ahora creo el archivo item_links.json y voy guardando los links de las publicaciones

                    for i in range(0, len(links_per_page)):
                        links['url' + str(y)] = links_per_page[i]
                        with open(path + "item_links.json", "w") as file:
                            json.dump(links, file)
                        print("Saved", links['url' + str(y)], "number of links saved:", y)
                        y += 1
    print("Links saved")


def downloaddata():
    # comienzo abriendo el archivo item_links.json para leerlo e ir obteniendo los links de las publicaciones

    with open('./download/ml/item_links.json', 'r') as f:
        domains = f.read()

    doms = json.loads(domains)

    count = 0  # count es el contador que indica en cual link arranca la descarga de imagenes

    links_number = 120000  # aca va el numero de links guardados en el json

    while count <= links_number:
        url_public = doms['url' + str(count)]
        print(url_public, count)

        response = requests.get(url_public, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # obtengo el id de la publicacion en la que me encuentro

        url_public_str = str(url_public)
        ides = re.findall('\d+', url_public_str)
        ides = list(map(int, ides))
        id_p = max(ides)

        # obtengo los datos del vehiculo

        data_vehicle = {}
        fields = []

        for li_tag in soup.findAll('ul', {'class': 'specs-list'}):
            for span_tag in li_tag.find_all('li'):
                value = span_tag.find('span').text
                field = span_tag.find('strong').text
                fields += [field]
                if value != '':
                    data_vehicle[field] = value

        # obtengo la marca y modelo del vehiculo

        data = []

        for i in range(0, len(soup.findAll('a', {'class': 'breadcrumb'}))):
            tag = soup.findAll('a', {'class': 'breadcrumb'})[i].text.replace('\t', '').replace('\n', '')
            data += [tag]

        data_vehicle['Marca'] = data[2]
        data_vehicle['Modelo'] = data[3]
        ibrand = data[2]
        imodel = data[3]

        path = './download/ml/' + str(ibrand).lower().replace(' ', '-') + '/' + str(id_p) + '/'

        if not os.path.exists(path):
            os.makedirs(path)

        # creo el meta.json donde van los datos del vehiculo

        with open(path + 'meta.json', 'w') as fp:
            json.dump(data_vehicle, fp)

        print("Created meta.json")

        # obtengo la ubicacion, solo para mostrarlo en pantalla

        i = 0
        place = []

        for div_tag in soup.findAll('div', {'class': 'location-info'}):
            place = div_tag.find('span').text
            i = i + 1
            if i > 0:
                break

        # obtengo los links de las imagenes de la publicacion en la que me encuentro

        q = 0
        images = []

        for i in range(0, len(soup.findAll('img'))):
            tag = soup.findAll('img')[i]
            if tag.get('data-srcset') is not None:
                image = tag.get('data-srcset').replace(' 2x', '').replace('webp', 'jpg')
                images += [image]
                q = q + 1

        y = 0

        # descargo las imagenes

        while y < q:
            urllib.request.urlretrieve(images[y], './download/ml/' + str(ibrand).lower().replace(' ', '-') + '/' + str(id_p) + '/' + str(ibrand).lower() + '_' + str(id_p) + '_' + str(y + 1) + '.jpg')
            print("Downloaded image", y + 1, "/", str(ibrand), str(imodel), "/",  place)
            y = y + 1

        count = count + 1

    print("Images downloaded")


path = './download/ml/item_links.json'

if not os.path.exists(path):
    savelinks()
    downloaddata()
else:
    downloaddata()
