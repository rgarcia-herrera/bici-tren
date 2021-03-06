# Bici-tren


Este repositorio contiene un marco para la modelación de sistemas de
movilidad urbana.

Consiste de una interfaz programática que permite expresar rasgos y
conductas de agentes que navegan mapas de ciudades.

Los mapas son de [OpenStreetMap](http://www.openstreetmap.org/), para
navegarlos se usa [brouter](http://brouter.de/), se visualizan con
[leaflet](http://leafletjs.com).

## Interfaz programática

Los agentes se modelan como clases de Python, de las que se instancían
objetos como procesos independientes que se comunican a través de una
base de datos.

Se usa [MongoDB](https://www.mongodb.com/what-is-mongodb), una base de
datos orientada a documentos con capacidades geoespaciales. Se pueden
encontrar agentes por proximidad (get_near()), dentro de áreas
(geo__within_box()), etc.

En [este script](html/ride.py) se instancía un agente y se le hace
recorrer una ruta obtenida de un archivo geojson.


## Instalación

Estas instrucciones funcionan en [bunsenlabs](http://bunsenlabs.org/), un derivado de
[debian](http://debian.org/). Para hacerlo funcionar en windows o en mac sugiero el uso de
una [máquina virtual](http://virtualbox.org) para instalar ahí debian,
y luego seguir estas instrucciones.

0. Dependencias de Debian/Bunsen

Instalar la base de datos y virtualenv para facilitar la gesitón de
dependencias de python.

```
$ sudo apt-get install python-virtualenv mongodb
```

1. Descargar o clonar este repositorio.

```
$ wget https://github.com/rgarcia-herrera/bici-tren/archive/master.zip
$ unzip master.zip
$ cd bici-tren
```

2. Descargar brouter.

```
$ wget http://brouter.de/brouter_bin/brouter_1_4_9.zip
$ unzip brouter_1_4_9.zip
```

3. Descargar tablas de ruteo. Con ese script se bajan *todas*, son 4.5 GB.

```
$ mkdir -p brouter/segments4
$ cd brouter/segments4
$ ./get_segments.sh
```

4. Instalar ambiente de Python

```
$ virtualenv venv
$ source venv/bin/activate
(venv) $  ambiente activado

(venv) $ pip install -r requirements.txt
[...]  # se instalan bibliotecas de python.
```


## Correr una simulación

1. Arrancar servidores.

```
$ ./servers.sh
```

2. Empezar simulación.

```
(venv) $ python ride.py -h


	usage: ride.py [-h] --geojson GEOJSON [--speed SPEED] [--id ID]

	ride bike at speed thru route

	optional arguments:
	  -h, --help         show this help message and exit
	  --geojson GEOJSON  A BRouter route in geojson format.
	  --speed SPEED      speed in meters per second, default=3.0
	  --id ID            bike id
```
