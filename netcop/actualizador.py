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
import syslog
import config


class Actualizador:
    version_actual = None
    version_ultima = None

    def __init__(self):
        self.version_actual = self.obtener_version_actual()
        self.version_disponible = self.obtener_version_disponible()

    def obtener_version_actual(self):
        '''
        Obtiene la ultima version de firmas aplicada.

        Los numeros de version aplicadas se guardan en el archivo definido
        en config.LOCAL_VERSION.
        '''
        version = None
        try:
            with open(config.LOCAL_VERSION, 'r') as f:
                # solo leo los primeros 64 bytes porque el numero de version
                # es un # SHA256
                version = f.read(64)
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
        syslog.syslog(syslog.LOG_DEBUG,
                      "Version aplicada %s" % self.version_actual)
        syslog.syslog(syslog.LOG_DEBUG,
                      "Ultima version disponible %s" % self.version_disponible)
        return self.version_actual != self.version_disponible

    def aplicar_actualizacion(self, clase):
        '''
        Guarda los cambios en la clase de trafico.
        '''
        pass

    def actualizar(self):
        '''
        Aplica la actualizacion de la base de firmas a la ultima version
        disponible.

        Actualiza el archivo que contiene la ultima version de firmas
        instaladas declarado en 'config.LOCAL_VERSION'
        '''
        syslog.syslog(
            syslog.LOG_DEBUG,
            "Actualizando a la versión '%s'" % self.version_disponible
        )

        # descarga y aplica la actualizacion
        # TODO transacciones
        for clase in self.descargar_actualizacion():
            self.aplicar_actualizacion(clase)

        # guarda ultima version en el archivo de versiones
        syslog.syslog(syslog.LOG_INFO, "La actualización fue exitosa")

        return True

    def obtener_version_disponible(self):
        '''
        Obtiene el numero de la ultima version de firmas disponibles desde el
        servidor de firmas.
        '''
        syslog.syslog(syslog.LOG_DEBUG,
                      "Ultima version disponible '%s'" % 'a')
        return 'a'

    def descargar_actualizacion(self):
        '''
        Descarga la ultima version de firmas y devuelve una lista de todas las
        clases de trafico.
        '''
        syslog.syslog(syslog.LOG_DEBUG, "Descargando ultima versión")
        return []


if __name__ == "__main__":
    syslog.openlog('actualizador')
    actualizador = Actualizador()
    if actualizador.hay_actualizacion():
        actualizador.actualizar()
    else:
        syslog.syslog(syslog.LOG_INFO, "No hay actualizaciones disponibles")
    syslog.closelog()
