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
from netcop import config
from netcop.models import ClaseTrafico


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
        syslog.syslog(syslog.LOG_DEBUG,
                      "Version aplicada: %s" % self.version_actual)
        syslog.syslog(syslog.LOG_DEBUG,
                      "Ultima version disponible: %s" % 
                      self.version_disponible)
        return self.version_actual != self.version_disponible

    def aplicar_actualizacion(self, clase):
        '''
        Guarda los cambios en la clase de trafico.
        '''
        assert clase.get('id') is not None
        actual = ClaseTrafico.get(clase['id'])
        # si la clase no existe
        if actual is None:
            actual = ClaseTrafico(**clase)
        # actualizo nombre y descripcion
        self.actualizar_colecciones(actual, clase)
        actual.load(**clase)
        actual.save()
        return actual

    def actualizar_colecciones(self, viejo, nuevo):
        '''
        Actualiza las colecciones de subredes y puertos de las clases de
        trafico de todos los grupos (inside o outside).

        El parametro *viejo* debe ser una instancia de ClaseTrafico y el
        parametro *nuevo* debe ser un diccionario que contenga la nueva
        informacion a actualizar.
        '''
        colecciones = (
            ('subredes_outside', 'subred', ClaseTrafico.OUTSIDE),
            ('subredes_inside', 'subred', ClaseTrafico.INSIDE),
            ('puertos_outside', 'puerto', ClaseTrafico.OUTSIDE),
            ('puertos_inside', 'puerto', ClaseTrafico.INSIDE),
        )
        for (coleccion, metodo, grupo) in colecciones:
            (agregar, quitar) = self.diferencia(coleccion, viejo, nuevo)
            for item in agregar:
                getattr(viejo, 'agregar_%s' % metodo)(item, grupo)
            for item in quitar:
                getattr(viejo, 'quitar_%s' % metodo)(item, grupo)


    def diferencia(self, nombre_coleccion, viejo, nuevo):
        '''
        Obtiene la diferencia entre dos colecciones indicando los items de la
        vieja coleccion que se tienen que borrar y cuales se tienen que agregar

        El parametro *viejo* debe ser una instancia de ClaseTrafico y el
        parametro *nuevo* debe ser un diccionario que contenga la nueva
        informacion a actualizar.

        Devuelve una tupla (agregar, quitar) donde agregar son los items que
        le faltan a la coleccion vieja y quitar son los items que le sobran a
        la collecion vieja
        '''
        new = nuevo.get(nombre_coleccion)
        old = getattr(viejo, nombre_coleccion)
        agregar = []
        quitar = []
        # agregar
        if new:
            if old:
                agregar = (set(new) - set(old))
            else:
                agregar = new
        # quitar
        if old:
            if new:
                quitar = (set(old) - set(new))
            else:
                quitar = old
        return (agregar, quitar)

    def actualizar(self):
        '''
        Aplica la actualizacion de la base de firmas a la ultima version
        disponible.

        Actualiza el archivo que contiene la ultima version de firmas
        instaladas declarado en 'config.LOCAL_VERSION'

        Devuelve verdadero si alguna clase fue modificada
        '''
        syslog.syslog(
            syslog.LOG_DEBUG,
            "Actualizando a la versión: %s" % self.version_disponible
        )

        # descarga y aplica la actualizacion
        # TODO transacciones
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
        return 'a'

    def descargar_actualizacion(self):
        '''
        Descarga la ultima version de firmas y devuelve una lista de todas las
        clases de trafico.
        '''
        syslog.syslog(syslog.LOG_DEBUG, "Descargando ultima versión")
        return []
