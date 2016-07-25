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
import sys
import syslog
import requests
from netcop import config, models


class Actualizador:
    '''
    Se encarga de mantener actualizada la base de datos de clases de trafico
    con la ultima version de firmas publicada.

    Para ello consulta cual es la ultima version al repositorio de firmas, si
    la version es distinta a la instalada, se descarga la nueva versión.
    '''
    version_actual = None
    version_ultima = None

    def __init__(self):
        '''
        Obtiene la ultima version aplicada y la ultima version disponible.
        '''

    def obtener_version_actual(self):
        '''
        Obtiene la ultima version de firmas aplicada.

        Los numeros de version aplicadas se guardan en el archivo definido
        en config.LOCAL_VERSION.
        '''
        version = None
        try:
            with open(config.LOCAL_VERSION, 'r') as f:
                # solo leo los primeros 65 bytes porque el numero de version
                # es un SHA256
                version = f.read(65)
        except:
            syslog.syslog(syslog.LOG_WARNING,
                          "No se pudo leer el archivo %s" %
                          config.LOCAL_VERSION)
        return version

    def guardar_version_actual(self):
        '''
        Guarda la ultima version de firmas aplicada.

        Los numeros de version aplicadas se guardan en el archivo definido
        en config.LOCAL_VERSION.
        '''
        try:
            with open(config.LOCAL_VERSION, 'w') as f:
                f.write(self.version_actual)
        except:
            syslog.syslog(syslog.LOG_CRIT,
                          "No se pudo escribir en el archivo %s" %
                          config.LOCAL_VERSION)

    def hay_actualizacion(self):
        '''
        Devuelve verdadero si existe una nueva version de firmas para
        actualizar.

        Lee la ultima version aplicada desde el archivo declarado en
        ´config.LOCAL_VERSION´
        '''
        self.version_actual = self.obtener_version_actual()
        self.version_disponible = self.obtener_version_disponible()
        syslog.syslog(
            syslog.LOG_DEBUG,
            "Version disponible: %s - Version aplicada: %s" %
            (self.version_disponible[0:6], self.version_actual[0:6])
        )
        return self.version_actual != self.version_disponible

    def aplicar_actualizacion(self, nueva):
        '''
        Guarda los cambios en la clase de trafico.
        '''
        assert nueva.get('id') is not None
        clase, creada = models.ClaseTrafico.create_or_get(
            id_clase=nueva["id"],
            nombre=nueva.get("nombre", ""),
            descripcion=nueva.get("descripcion", ""),
            activa=nueva.get("activa", True),
        )

        query = models.ClaseTrafico.select().where(
            models.ClaseTrafico.id_clase == nueva['id']
        )
        # si la clase existe actualizo sus campos
        if not creada:
            clase = query.first()
            clase.nombre = nueva.get("nombre", "")
            clase.descripcion = nueva.get("descripcion", "")
            clase.activa = nueva.get("activa", True)
            clase.save()
        self.actualizar_colecciones(clase, nueva)
        return clase

    def actualizar_colecciones(self, clase, nueva):
        '''
        Actualiza las listas de subredes y puertos de la clase de trafico.
        '''
        redes = (('subredes_outside', models.OUTSIDE),
                 ('subredes_inside', models.INSIDE))
        puertos = (('puertos_outside', models.OUTSIDE),
                   ('puertos_inside', models.INSIDE))

        models.ClaseCIDR.delete().where(models.ClaseCIDR.clase == clase)
        models.ClasePuerto.delete().where(models.ClasePuerto.clase == clase)

        for lista, grupo in redes:
            for item in nueva.get(lista, []):
                (direccion, prefijo) = item.split('/')
                cidr = models.CIDR.get_or_create(direccion=direccion,
                                                 prefijo=prefijo)[0]
                models.ClaseCIDR.create_or_get(clase=clase, cidr=cidr,
                                               grupo=grupo)

        for lista, grupo in puertos:
            for item in nueva.get(lista, []):
                (numero, proto) = item.split('/')
                protocolo = self.protocolo(proto)
                puerto = models.Puerto.get_or_create(numero=numero,
                                                     protocolo=protocolo)[0]
                models.ClasePuerto.create_or_get(clase=clase, puerto=puerto,
                                                 grupo=grupo)

    def protocolo(self, string):
        '''
        Obtiene el numero de protocolo en base a una cadena de caracteres.

        Retornos
        ---------------
          * 6 - TCP | tcp
          * 17 - UDP | udp
          * 0 en cualquier otro caso.
        '''
        if string.lower() == 'tcp':
            return 6
        elif string.lower() == 'udp':
            return 17
        return 0

    @models.db.atomic()
    def actualizar(self):
        '''
        Aplica la actualizacion de la base de firmas a la ultima version
        disponible.

        Actualiza el archivo que contiene la ultima version de firmas
        instaladas declarado en 'config.LOCAL_VERSION'

        Devuelve verdadero si alguna clase fue modificada
        '''
        syslog.syslog(syslog.LOG_DEBUG, "Actualizando a la version: %s" %
                                        self.version_disponible[0:6])

        # descarga y aplica la actualizacion
        for clase in self.descargar_actualizacion():
            self.aplicar_actualizacion(clase)

        # guarda ultima version en el archivo de versiones
        self.version_actual = self.version_disponible
        self.guardar_version_actual()
        syslog.syslog(syslog.LOG_INFO, "La actualización fue exitosa")

    def obtener_version_disponible(self):
        '''
        Obtiene el numero de la ultima version de firmas disponibles desde el
        servidor de firmas.
        '''
        return self.obtener_servidor(config.URL_VERSION)["version"]

    def descargar_actualizacion(self):
        '''
        Descarga la ultima version de firmas y devuelve una lista de todas las
        clases de trafico.
        '''
        syslog.syslog(syslog.LOG_DEBUG, "Descargando ultima versión")
        return self.obtener_servidor(config.URL_DOWNLOAD)["clases"]

    def obtener_servidor(self, url):
        '''
        Obtiene informacion del servidor de actualizaciones
        '''
        try:
            r = requests.get(url)
            if 200 <= r.status_code < 300:
                return r.json()
            raise Exception("Respuesta del servidor: %d" % r.status_code)
        except:
            sys.stderr.write("No se pudo actualizar: %s no está disponible\n" %
                             url)
            syslog.syslog(syslog.LOG_CRIT,
                          "No se pudo actualizar: %s no está disponible" % url)
            raise
