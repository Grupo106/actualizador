# -*- coding: utf-8 -*-
'''
Configuracion del modulo de actualizacion
'''

# Ruta del archivo que contiene la ultima version descargada
LOCAL_VERSION = '/tmp/actualizador'

# URL donde se consultara el ultimo número de versión disponible
URL_VERSION = 'http://localhost:8000/version'

# URL donde se descargará la ultima versión de firmas
URL_DOWNLOAD = 'http://localhost:8000/download'

# Cadena de conexion con base de datos Postgres
BD_STRING = ''

# Usuario base de datos
BD_USER = ''

# Contraseña base de datos
BD_PASSWORD = ''
