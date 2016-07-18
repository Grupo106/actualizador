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
import ConfigParser

def hay_actualizacion():
    '''
    Devuelve verdadero si existe una nueva version de firmas para actualizar.
    '''
    # leer archivo de ultima version aplicada
    version_actual = None
    syslog.syslog(syslog.LOG_DEBUG, "Version actual '%s'" % version_actual)
    return version_actual != consultar_ultima_version()


def actualizar():
    '''
    Aplica la actualizacion de la base de firmas a la ultima version
    disponible.
    '''
    clases = descargar_actualizacion()
    syslog.syslog(syslog.LOG_DEBUG,
                  "Actualizando a la ultima versión de firmas")
    # escribir en el archivo la ultima version aplicada


def consultar_ultima_version():
    '''
    Obtiene el numero de la ultima version de firmas disponibles desde el
    servidor de firmas.
    '''
    version = None
    syslog.syslog(syslog.LOG_DEBUG, "Ultima version disponible '%s'" % version)
    return version


def descargar_actualizacion():
    '''
    Descarga la ultima version de firmas y devuelve una lista de todas las
    clases de trafico.
    '''
    syslog.syslog(syslog.LOG_DEBUG, "Descargando ultima versión")
    pass


if __name__ == "__main__":
    syslog.openlog()
    if hay_actualizacion():
        actualizar()
    else:
        syslog.syslog(syslog.LOG_DEBUG, "No hay actualizaciones disponibles")
    syslog.closelog()
