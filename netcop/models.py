# -*- coding: utf-8 -*-
'''
Este modulo define los objetos que seran guardados en la base de datos.
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

    class Meta:
        database = db
        db_table = u'puerto'


class ClaseCIDR(models.Model):
    '''
    Relaciona una clase de trafico con un CIDR.
    '''
    id_clase = models.ForeignKeyField(ClaseTrafico)
    id_cidr = models.ForeignKeyField(CIDR)
    grupo = models.FixedCharField(max_length=1)

    class Meta:
        database = db
        db_table = u'clase_cidr'
        primary_key = models.CompositeKey('id_clase', 'id_cidr')


class ClasePuerto(models.Model):
    '''
    Relaciona una clase de trafico con un puerto.
    '''
    id_clase = models.ForeignKeyField(ClaseTrafico)
    id_puerto = models.ForeignKeyField(Puerto)
    grupo = models.FixedCharField(max_length=1)

    class Meta:
        database = db
        db_table = u'clase_puerto'
        primary_key = models.CompositeKey('id_clase', 'id_puerto')
