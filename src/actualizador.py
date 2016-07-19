#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Este modulo se encarga de mantener actualizada la base de datos de clases de
trafico con la ultima version de firmas publicada.

Para ello consulta cual es la ultima version al repositorio de firmas, si la
version es distinta a la instalada, se descarga la nueva versión.

Las versiones se descargan en formato JSON.

@author Yonatan Romero
@url https://github.com/grupo106/actualizador

(c) 2016. Netcop. Universidad Nacional de la Matanza.
'''
import json
import syslog
import config
import requests
import psycopg2


def hay_actualizacion():
    '''
    Devuelve verdadero si existe una nueva version de firmas para actualizar.

    Lee la ultima version aplicada desde el archivo declarado en
    ´config.LOCAL_VERSION´
    '''
    try:
        with open(config.LOCAL_VERSION, 'r') as f:
            # solo leo los primeros 64 bytes porque el numero de version es un
            # SHA256
            actual = f.read(64)
    except:
        actual = None
        syslog.syslog(syslog.LOG_WARNING, "No se pudo leer el archivo %s" %
                      config.LOCAL_VERSION)
    ultima = consultar_ultima_version()
    syslog.syslog(syslog.LOG_DEBUG, "Version actual '%s'" % actual)
    syslog.syslog(syslog.LOG_DEBUG, "Ultima version disponible '%s'" % ultima)
    return actual != ultima


def aplicar_actualizacion(clase):
    '''
    Guarda los cambios en la clase de trafico.
    '''
    pass


def actualizar():
    '''
    Aplica la actualizacion de la base de firmas a la ultima version
    disponible.

    Actualiza el archivo que contiene la ultima version de firmas instaladas
    declarado en 'config.LOCAL_VERSION'
    '''
    version = consultar_ultima_version()
    syslog.syslog(syslog.LOG_DEBUG, "Actualizando a la versión '%s'" % version)

    # descarga y aplica la actualizacion
    for clase in descargar_actualizacion():
        aplicar_actualizacion(clase)

    # guarda ultima version en el archivo de versiones
    try:
        with open(config.LOCAL_VERSION, 'w') as f:
            f.write(version)
    except:
        syslog.syslog(syslog.LOG_CRIT, "No se pudo escribir en el archivo %s" %
                      config.LOCAL_VERSION)
    syslog.syslog(syslog.LOG_INFO, "La actualización fue exitosa")

    # TODO transacciones
    return True


def consultar_ultima_version():
    '''
    Obtiene el numero de la ultima version de firmas disponibles desde el
    servidor de firmas.
    '''
    return 'a'


def descargar_actualizacion():
    '''
    Descarga la ultima version de firmas y devuelve una lista de todas las
    clases de trafico.
    '''
    syslog.syslog(syslog.LOG_DEBUG, "Descargando ultima versión")
    return []


if __name__ == "__main__":
    syslog.openlog('actualizador')
    if hay_actualizacion():
        actualizar()
    else:
        syslog.syslog(syslog.LOG_INFO, "No hay actualizaciones disponibles")
    syslog.closelog()
