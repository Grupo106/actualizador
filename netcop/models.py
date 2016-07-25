# -*- coding: utf-8 -*-
'''
Este modulo define los objetos que seran guardados en la base de datos.

Utiliza el paquete *peewee* para el mapeo objeto-relacional. Permite realizar
las consultas a la base de datos en lenguaje python de forma sencilla sin
necesidad de escribir codigo SQL.
'''
import peewee as models
from netcop import config

# Identificador de grupo para servicios que esten en la red local
INSIDE = 'i'
# Identificador de grupo para servicios que esten en Internet
OUTSIDE = 'o'

# Declaro parametros de conexion de la base de datos
db = models.PostgresqlDatabase(config.BD_DATABASE,
                               host=config.BD_HOST,
                               user=config.BD_USER,
                               password=config.BD_PASSWORD)


class ClaseTrafico(models.Model):
    '''
    Una clase de trafico almacena los patrones a reconocer en los paquetes
    capturados.
    '''
    id_clase = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=32)
    descripcion = models.CharField(max_length=160)
    tipo = models.SmallIntegerField(default=0)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return u"%d: %s" % (self.id_clase, self.nombre)

    class Meta:
        database = db
        db_table = u'clase_trafico'


class CIDR(models.Model):
    '''
    El CIDR representa una subred. Se compone de una dirección de red y una
    máscara de subred representada con un prefijo que indica la cantidad de
    bits que contiene la máscara.

    Por ejemplo la subred 10.200.0.0 con máscara de subred 255.255.0.0 se
    representa como 10.200.0.0/16 siendo el prefijo 16, porque la mascara
    contiene 16 bits en uno.

    Si todos los bits de la mascara de subred están en uno representan a una
    red de host y el prefijo es 32.
    '''
    id_cidr = models.IntegerField(primary_key=True)
    direccion = models.CharField(max_length=32)
    prefijo = models.SmallIntegerField(default=0)

    def __str__(self):
        return u"%d: %s/%d" % (self.id_cidr, self.direccion, self.prefijo)

    class Meta:
        database = db
        db_table = u'cidr'


class Puerto(models.Model):
    '''
    Un puerto identifica una aplicacion en un host. Sirve para mantener muchas
    conversaciones al mismo tiempo con distintas aplicaciones.

    Los puertos se componen de un numero de 2 bytes sin signo (rango entre 0 y
    65535) y un protocolo que puede ser 6 (TCP) o 17 (UDP).
    '''
    id_puerto = models.IntegerField(primary_key=True)
    numero = models.IntegerField()
    protocolo = models.SmallIntegerField(default=0)

    def __str__(self):
        proto = str(self.protocolo)
        if self.protocolo == 6:
            proto = "TCP"
        elif self.protocolo == 17:
            proto = "UDP"
        return u"%d: %s/%d" % (self.id_puerto, self.numero, proto)

    class Meta:
        database = db
        db_table = u'puerto'


class ClaseCIDR(models.Model):
    '''
    Relaciona una clase de trafico con un CIDR.
    '''
    clase = models.ForeignKeyField(ClaseTrafico, related_name='redes',
                                   db_column='id_clase')
    cidr = models.ForeignKeyField(CIDR, related_name='clases',
                                  db_column='id_cidr')
    grupo = models.FixedCharField(max_length=1)

    def __str__(self):
        return u"clase=%d cidr=%d" % (self.clase.id_clase,
                                      self.cidr.id_cidr)

    class Meta:
        database = db
        db_table = u'clase_cidr'
        primary_key = models.CompositeKey('clase', 'cidr')


class ClasePuerto(models.Model):
    '''
    Relaciona una clase de trafico con un puerto.
    '''
    clase = models.ForeignKeyField(ClaseTrafico, related_name='puertos',
                                   db_column='id_clase')
    puerto = models.ForeignKeyField(Puerto, related_name='clases',
                                    db_column='id_puerto')
    grupo = models.FixedCharField(max_length=1)

    def __str__(self):
        return u"clase=%d puerto=%d" % (self.clase.id_clase,
                                        self.puerto.id_puerto)

    class Meta:
        database = db
        db_table = u'clase_puerto'
        primary_key = models.CompositeKey('clase', 'puerto')
