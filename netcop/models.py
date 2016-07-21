# -*- coding: utf-8 -*-
'''
Este modulo define los objetos que seran guardados en la base de datos.
'''

class ClaseTrafico:
    '''
    Una clase de trafico almacena los patrones a reconocer en los paquetes
    capturados.
    '''
    # Identificador de grupo para servicios que esten en la red local
    INSIDE = 'i'
    # Identificador de grupo para servicios que esten en Internet
    OUTSIDE = 'o'

    def __init__(self, **kwargs):
        '''
        Crea una instancia de la clase de trafico a traves de los parametros
        con nombre.
        '''
        self.load(**kwargs)

    def save(self):
        '''
        Guarda la clase de trafico en la base de datos.
        '''
        print("INSERT INTO clase_trafico(id, nombre, descripcion) "
              "VALUES (%d, %s, %s)"
              % (self.id, self.nombre, self.descripcion))
        return None

    def load(self, **kwargs):
        '''
        Carga atributos desde parametros por nombre.
        '''
        self.id = kwargs.get('id')
        self.nombre = kwargs.get('nombre', '')
        self.descripcion = kwargs.get('descripcion', '')
        self.subredes_outside = kwargs.get('subredes_outside')
        self.subredes_inside = kwargs.get('subredes_inside')
        self.puertos_outside = kwargs.get('puertos_outside')
        self.puertos_inside = kwargs.get('puertos_inside')
        self.activa = kwargs.get('activa', True)

    @classmethod
    def get(self, _id):
        '''
        Obtiene una clase de trafico por su id. Si la clase no existe devuelve
        None.

        La clase de trafico debe estar marcada como clase de trafico de sistema
        en la base de datos.
        '''
        return None

    def agregar_subred(self, subred, tipo):
        '''
        Agrega subred a la coleccion de subredes en la base de datos. El tipo
        puede ser INSIDE o OUTSIDE
        '''
        print("INSERT INTO clase_cidr(id, nombre, descripcion) "
              "VALUES (%d, %s, %s)"
              % (self.id, self.nombre, self.descripcion))

    def agregar_puerto(self, subred, tipo):
        '''
        Agrega puerto a la coleccion de puertos en la base de datos. El tipo
        puede ser INSIDE o OUTSIDE
        '''
        print("INSERT INTO clase_puerto(id, nombre, descripcion) "
              "VALUES (%d, %s, %s)"
              % (self.id, self.nombre, self.descripcion))

    def quitar_subred(self, subred, tipo):
        '''
        Quita la subred de la coleccion de subredes en la base de datos. El
        tipo puede ser INSIDE o OUTSIDE
        '''
        print("DELETE FROM clase_cidr WHERE id=%d" % self.id)

    def quitar_puerto(self, subred, tipo):
        '''
        Agrega subred a la coleccion de subredes en la base de datos. El tipo
        puede ser INSIDE o OUTSIDE
        '''
        print("DELETE FROM clase_puerto WHERE id=%d" % self.id)
