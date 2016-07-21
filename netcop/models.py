'''
Este modulo define los objetos que seran guardados en la base de datos.
'''

class ClaseTrafico:
    '''
    Una clase de trafico almacena los patrones a reconocer en los paquetes
    capturados.
    '''

    def __init__(self, **kwargs):
        '''
        Crea una instancia de la clase de trafico a traves de los parametros
        con nombre.
        '''
        self.id = kwargs.get('id')
        self.nombre = kwargs.get('nombre')
        self.descripcion = kwargs.get('descripcion')
        self.subredes_outside = kwargs.get('subredes_outside')
        self.subredes_inside = kwargs.get('subredes_inside')
        self.puertos_outside = kwargs.get('puertos_outside')
        self.puertos_inside = kwargs.get('puertos_inside')
        self.habilitada = kwargs.get('habilitada', True)

    def save(self):
        '''
        Guarda la clase de trafico en la base de datos.
        '''
        return None

    @classmethod
    def get(self, _id):
        '''
        Obtiene una clase de trafico por su id. Si la clase no existe devuelve
        None.

        La clase de trafico debe estar marcada como clase de trafico de sistema
        en la base de datos.
        '''
        return None
