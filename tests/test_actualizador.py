# -*- coding: utf-8 -*-
'''
Pruebas del modulo actualizador.

Se prueban todos los metodos de la clase ´Actualizador´
'''
import netcop
import unittest
from mock import patch, mock_open, Mock
from netcop.actualizador import models, config


class ActualizadorTests(unittest.TestCase):

    def setUp(self):
        models.db.create_tables(
            [models.ClaseTrafico, models.CIDR, models.Puerto, models.ClaseCIDR,
             models.ClasePuerto],
            safe=True)
        self.actualizador = netcop.Actualizador()

    @patch.object(netcop.Actualizador, 'obtener_version_actual')
    @patch.object(netcop.Actualizador, 'obtener_version_disponible')
    def test_hay_actualizacion(self, mock_disponible, mock_actual):
        '''
        Prueba que el metodo hay_actualizacion devuelva verdadero cuando
        la ultima version aplicada sea distinta a la ultima version disponible.
        '''
        # preparo datos
        mock_actual.return_value = 'a'
        mock_disponible.return_value = 'b'
        # llamo metodo a probar
        assert self.actualizador.hay_actualizacion()

        # preparo datos
        mock_actual.return_value = 'b'
        # llamo metodo a probar
        assert not self.actualizador.hay_actualizacion()

    @patch('netcop.actualizador.actualizador.open', create=True)
    def test_obtener_version_actual(self, mock):
        '''
        Prueba que se lea el archivo que almacena la ultima version aplicada
        definido en config.LOCAL_VERSION.
        '''
        # preparo datos
        mock_open(mock, read_data='v1')
        # llamo metodo a probar
        version = self.actualizador.obtener_version_actual()
        # verifico que todo este bien
        mock.assert_called_once_with(config.NETCOP['local_version'], 'r')
        assert version == 'v1'

    @patch('syslog.syslog')
    @patch('netcop.actualizador.actualizador.open', create=True)
    def test_obtener_version_actual_fail(self, mock_open, mock_syslog):
        '''
        Prueba el tratamiento del error en caso de no poder leer el archivo de
        versiones definido en config.LOCAL_VERSION.
        '''
        # preparo datos
        mock_open.side_effect = IOError()
        # llamo metodo a probar
        version = self.actualizador.obtener_version_actual()
        # verifico que todo este bien
        mock_open.assert_called_once_with(config.NETCOP['local_version'], 'r')
        mock_syslog.assert_called_once()
        assert version is None

    @patch('netcop.actualizador.actualizador.open', create=True)
    def test_guardar_version_actual(self, mock):
        '''
        Prueba guardar la ultima version aplicada en el archivo de versiones
        definido en config.LOCAL_VERSION.
        '''
        # preparo datos
        m = mock_open(mock)
        self.actualizador.version_actual = 'pepe'
        # llamo metodo a probar
        self.actualizador.guardar_version_actual()
        # verifico que todo este bien
        m.assert_called_once_with(config.NETCOP['local_version'], 'w')
        handle = m()
        handle.write.assert_called_once_with('pepe')

    @patch('syslog.syslog')
    @patch('netcop.actualizador.actualizador.open', create=True)
    def test_guardar_version_actual_fail(self, mock_open, mock_syslog):
        '''
        Prueba el tratamiento del error en caso de no poder guardar la ultima
        version en el archivo de versiones definido en config.LOCAL_VERSION.
        '''
        # preparo datos
        mock_open.side_effect = IOError()
        # llamo metodo a probar
        self.actualizador.guardar_version_actual()
        # verifico que todo este bien
        mock_open.assert_called_once_with(config.NETCOP['local_version'], 'w')
        mock_syslog.assert_called_once()

    def test_actualizar(self):
        '''
        Prueba el metodo actualizar.
        '''
        # preparo datos
        self.actualizador.version_actual = 'a'
        self.actualizador.version_disponible = 'b'

        mock_descargar = Mock()
        mock_descargar.return_value = [
            {
                'nombre': 'foo',
                'descripcion': 'bar'
            },
            {
                'nombre': 'bar',
                'descripcion': 'bar'
            },
        ]
        self.actualizador.descargar_actualizacion = mock_descargar

        mock_aplicar = Mock()
        mock_aplicar.return_value = True
        self.actualizador.aplicar_actualizacion = mock_aplicar
        # llamo metodo a probar
        self.actualizador.actualizar()
        # verifico que todo este bien
        mock_descargar.assert_called_once()
        mock_aplicar.assert_called()
        assert mock_aplicar.call_count == 2
        assert self.actualizador.version_actual == 'b'

    def test_aplicar_actualizacion_nueva(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase inexistente
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            clase = {
                'id': 60606060,
                'nombre': 'pepe',
                'descripcion': 'clase de prueba',
                'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24'],
                'subredes_inside': ['3.3.3.3/32'],
                'puertos_outside': ['80/tcp', '443/tcp'],
                'puertos_inside': ['1024/udp'],
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)
            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            assert saved.nombre == 'pepe'
            assert saved.descripcion == 'clase de prueba'
            redes = (('1.1.1.1', 32, models.OUTSIDE),
                     ('2.2.2.0', 24, models.OUTSIDE),
                     ('3.3.3.3', 32, models.INSIDE))
            puertos = ((80, 6, models.OUTSIDE),
                       (443, 6, models.OUTSIDE),
                       (1024, 17, models.INSIDE))
            # verifico redes
            for (direccion, prefijo, grupo) in redes:
                assert (models.ClaseCIDR
                        .select()
                        .join(models.CIDR)
                        .where(models.ClaseCIDR.clase == 60606060,
                               models.CIDR.direccion == direccion,
                               models.CIDR.prefijo == prefijo,
                               models.ClaseCIDR.grupo == grupo)
                        .get())
            # verifico puertos
            for (numero, protocolo, grupo) in puertos:
                assert (models.ClasePuerto
                        .select()
                        .join(models.Puerto)
                        .where(models.ClasePuerto.clase == 60606060,
                               models.Puerto.numero == numero,
                               models.Puerto.protocolo == protocolo,
                               models.ClasePuerto.grupo == grupo)
                        .get())
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_deshabilitar(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase que se deshabilito
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='pepe',
                descripcion='clase de prueba',
                activa=True
            )
            clase = {
                'id': 60606060,
                'nombre': 'pepe',
                'descripcion': 'clase de prueba',
                'activa': False
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)
            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            assert not saved.activa
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_nombre(self):
        '''
        Prueba el metodo aplicar_actualizacion cambiando el nombre y
        descripcion de la clase.
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='pepe',
                descripcion='clase de prueba',
                activa=True
            )
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'activa': True
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)
            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            assert saved.nombre == 'foo'
            assert saved.descripcion == 'bar'
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_sin_cambios(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que no
        tenga cambios
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='foo',
                descripcion='bar',
                activa=True
            )
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'activa': True
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)
            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            assert saved.nombre == 'foo'
            assert saved.descripcion == 'bar'
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_nueva_subred(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga nuevas subredes
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            clase = models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='foo',
                descripcion='bar'
            )
            cidr = [models.CIDR.create(direccion='1.1.1.1', prefijo=32),
                    models.CIDR.create(direccion='2.2.2.0', prefijo=32)]
            for item in cidr:
                models.ClaseCIDR.create(clase=clase, cidr=item,
                                        grupo=models.OUTSIDE)
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24', '3.3.0.0/20'],
                'subredes_inside': ['4.4.4.4/32'],
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)

            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            redes = (('1.1.1.1', 32, models.OUTSIDE),
                     ('2.2.2.0', 24, models.OUTSIDE),
                     ('3.3.0.0', 20, models.OUTSIDE),
                     ('4.4.4.4', 32, models.INSIDE))
            for (direccion, prefijo, grupo) in redes:
                assert (saved.redes
                        .join(models.CIDR)
                        .where(models.CIDR.direccion == direccion,
                               models.CIDR.prefijo == prefijo,
                               models.ClaseCIDR.grupo == grupo)
                        .get())
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_nuevo_puerto(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga nuevos puertos
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            clase = models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='foo',
                descripcion='bar',
            )
            puertos = [models.Puerto.create(numero=80, protocolo=6),
                       models.Puerto.create(numero=80, protocolo=17)]
            for item in puertos:
                models.ClasePuerto.create(clase=clase, puerto=item,
                                          grupo=models.OUTSIDE)
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'puertos_outside': ['443/tcp', '80/tcp'],
                'puertos_inside': ['1024/udp', '53']
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)

            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            puertos = ((443,   6, models.OUTSIDE),
                       (80,    6, models.OUTSIDE),
                       (1024, 17, models.INSIDE),
                       (53, 0, models.INSIDE),)
            for (numero, protocolo, grupo) in puertos:
                assert (saved.puertos
                        .join(models.Puerto)
                        .where(models.Puerto.numero == numero,
                               models.Puerto.protocolo == protocolo,
                               models.ClasePuerto.grupo == grupo)
                        .get())
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_clase_personalizada(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase que no es de
        sistema. No debería modificarla
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            clase = models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='foo',
                descripcion='bar',
                tipo=1  # tipo personalizada
            )
            puertos = [models.Puerto.create(numero=80, protocolo=6),
                       models.Puerto.create(numero=443, protocolo=6)]
            for item in puertos:
                models.ClasePuerto.create(clase=clase, puerto=item,
                                          grupo=models.OUTSIDE)
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'puertos_outside': ['443/tcp', '80/tcp'],
                'puertos_inside': ['1024/udp', '53']
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)

            # verifico que no se haya modificado nada
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            puertos_si = ((443,   6, models.OUTSIDE),
                          (80,    6, models.OUTSIDE))
            puertos_no = ((1024, 17, models.INSIDE),
                          (53, 0, models.INSIDE),)
            for (numero, protocolo, grupo) in puertos_si:
                assert (saved.puertos
                        .join(models.Puerto)
                        .where(models.Puerto.numero == numero,
                               models.Puerto.protocolo == protocolo,
                               models.ClasePuerto.grupo == grupo)
                        .get())
            for (numero, protocolo, grupo) in puertos_no:
                assert not (saved.puertos
                            .join(models.Puerto)
                            .where(models.Puerto.numero == numero,
                                   models.Puerto.protocolo == protocolo,
                                   models.ClasePuerto.grupo == grupo)
                            .exists())
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_eliminar_subred(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga menos subredes
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            clase = models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='foo',
                descripcion='bar'
            )
            cidr = [models.CIDR.create(direccion='1.1.1.1', prefijo=32),
                    models.CIDR.create(direccion='2.2.2.0', prefijo=24),
                    models.CIDR.create(direccion='3.3.0.0', prefijo=20)]
            for item in cidr:
                models.ClaseCIDR.create(clase=clase, cidr=item,
                                        grupo=models.OUTSIDE)
            inside = models.CIDR.create(direccion='4.4.4.4', prefijo=32)
            models.ClaseCIDR.create(clase=clase, cidr=inside,
                                    grupo=models.INSIDE)
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'subredes_outside': ['1.1.1.1/32']
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)

            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            assert (saved.redes
                    .join(models.CIDR)
                    .where(models.CIDR.direccion == '1.1.1.1',
                           models.CIDR.prefijo == 32,
                           models.ClaseCIDR.grupo == models.OUTSIDE)
                    .get())
            redes = (('2.2.2.0', 24, models.OUTSIDE),
                     ('3.3.0.0', 20, models.OUTSIDE),
                     ('4.4.4.4', 32, models.INSIDE))
            for (direccion, prefijo, grupo) in redes:
                with self.assertRaises(models.ClaseCIDR.DoesNotExist):
                    (saved.redes
                          .join(models.CIDR)
                          .where(models.CIDR.direccion == direccion,
                                 models.CIDR.prefijo == prefijo,
                                 models.ClaseCIDR.grupo == grupo)
                          .get())
            # descarto cambios en la base de datos
            transaction.rollback()

    def test_aplicar_actualizacion_eliminar_puerto(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga menos puertos
        '''
        # creo transaccion para descartar cambios generados en la base
        with models.db.atomic() as transaction:
            # preparo datos
            clase = models.ClaseTrafico.create(
                id_clase=60606060,
                nombre='foo',
                descripcion='bar'
            )
            puertos = [models.Puerto.create(numero=443, protocolo=6),
                       models.Puerto.create(numero=80, protocolo=6)]
            for item in puertos:
                models.ClasePuerto.create(clase=clase, puerto=item,
                                          grupo=models.OUTSIDE)
            inside = models.Puerto.create(numero=1024, protocolo=17)
            models.ClasePuerto.create(clase=clase, puerto=inside,
                                      grupo=models.OUTSIDE)
            clase = {
                'id': 60606060,
                'nombre': 'foo',
                'descripcion': 'bar',
                'puertos_inside': ['1024/udp']
            }
            # llamo metodo a probar
            self.actualizador.aplicar_actualizacion(clase)

            # verifico que todo este bien
            saved = models.ClaseTrafico.get(
                models.ClaseTrafico.id_clase == 60606060
            )
            assert (saved.puertos
                    .join(models.Puerto)
                    .where(models.Puerto.numero == 1024,
                           models.Puerto.protocolo == 17,
                           models.ClasePuerto.grupo == models.INSIDE)
                    .get())
            puertos = ((443, 6, models.OUTSIDE), (80, 6, models.OUTSIDE))
            for (numero, protocolo, grupo) in puertos:
                with self.assertRaises(models.ClasePuerto.DoesNotExist):
                    (saved.puertos
                          .join(models.Puerto)
                          .where(models.Puerto.numero == numero,
                                 models.Puerto.protocolo == protocolo,
                                 models.ClasePuerto.grupo == grupo)
                          .get())
            # descarto cambios en la base de datos
            transaction.rollback()

    @patch('requests.get')
    def test_consultar_version_disponible(self, mock_get):
        '''
        Prueba obtener la ultima version disponible desde el servidor.
        '''
        # preparo datos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={'version': 'a'})
        mock_get.return_value = mock_response
        # llamo metodo a probar
        version = self.actualizador.obtener_version_disponible()
        # verifico que todo este bien
        assert version == 'a'

    @patch('requests.get')
    def test_consultar_version_disponible_error(self, mock_get):
        '''
        Prueba el tratamiento de error al obtener la ultima version disponible
        '''
        # preparo datos
        mock_get.side_effect = IOError()
        # llamo metodo a probar
        with self.assertRaises(IOError):
            self.actualizador.obtener_version_disponible()

        # preparo datos
        mock_get.side_effect = None
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 500
        # llamo metodo a probar
        with self.assertRaises(Exception):
            self.actualizador.obtener_version_disponible()

    @patch('requests.get')
    def test_descargar_actualizacion(self, mock_get):
        '''
        Prueba la descarga de la ultima version desde el servidor. Debe
        retornar una lista de clases de trafico en forma de diccionarios.
        '''
        # preparo datos
        clases = [
            {
                'id': 1,
                'nombre': 'foo',
                'descripcion': 'bar',
            },
            {
                'id': 2,
                'nombre': 'fulano',
                'descripcion': 'mengano',
            },
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={'clases': clases})
        mock_get.return_value = mock_response
        # llamo metodo a probar
        descarga = self.actualizador.descargar_actualizacion()
        # verifico que todo este bien
        for clase in clases:
            assert clase in descarga

    @patch('requests.get')
    def test_descargar_actualizacion_error(self, mock_get):
        '''
        Prueba el tratamiento de error al descargar la ultima version
        '''
        # preparo datos
        mock_get.side_effect = IOError()
        # llamo metodo a probar
        with self.assertRaises(IOError):
            self.actualizador.descargar_actualizacion()

        # preparo datos
        mock_get.side_effect = None
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 500
        # llamo metodo a probar
        with self.assertRaises(Exception):
            self.actualizador.descargar_actualizacion()
