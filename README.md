# scriptml
Script en python para descargar todas las imagenes de automoviles y sus características de la pagina mercadolibre.com.ar

ml.py -> Guarda primero todos los links en un archivo .json de manera que si el servidor te echa por reiteradas consultas se puede arrancar desde donde lo dejaste.

ml2.py -> Consigue el mismo resultado que ml.py pero este no va guardando los links en un archivo .json por lo que si el servidor te echa se tiene que arrancar desde el principio.

ml3.py -> Este script a diferencia de los dos anteriores no trabaja aplicando filtros, de modo que se pueden descargar las imagenes de 2016 publicaciones debido a la restriccion de Mercado Libre.

