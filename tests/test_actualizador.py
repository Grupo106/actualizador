# -*- coding: utf-8 -*-
'''
Pruebas del modulo actualizador.

Se prueban todos los metodos de la clase ´Actualizador´
'''
import netcop
import unittest
from mock import patch, mock_open, Mock, call
from netcop import models


class ActualizadorTests(unittest.TestCase):

    def setUp(self):
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

    @patch('netcop.actualizador.open', create=True)
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
        mock.assert_called_once_with(netcop.config.LOCAL_VERSION, 'r')
        assert version == 'v1'

    @patch('syslog.syslog')
    @patch('netcop.actualizador.open', create=True)
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
        mock_open.assert_called_once_with(netcop.config.LOCAL_VERSION, 'r')
        mock_syslog.assert_called_once()
        assert version is None

    @patch('netcop.actualizador.open', create=True)
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
        m.assert_called_once_with(netcop.config.LOCAL_VERSION, 'w')
        handle = m()
        handle.write.assert_called_once_with('pepe')

    @patch('syslog.syslog')
    @patch('netcop.actualizador.open', create=True)
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
        mock_open.assert_called_once_with(netcop.config.LOCAL_VERSION, 'w')
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

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_deshabilitar(self, mock_get, mock_save):
        '''
        Prueba el metodo aplicar_actualizacion con una clase que se deshabilito
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='pepe',
            descripcion='clase de prueba',
            subredes_outside=['1.1.1.1/32', '2.2.2.0/24'],
            activa=True
        )

        clase = {
            'id': 1,
            'nombre': 'pepe',
            'descripcion': 'clase de prueba',
            'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24'],
            'activa': False
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_get.assert_called_once_with(1)
        mock_save.assert_called_once()
        assert not ret.activa

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_nombre(self, mock_get, mock_save):
        '''
        Prueba el metodo aplicar_actualizacion cambiando el nombre o
        descripcion de la clase.
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='pepe',
            descripcion='clase de prueba',
            subredes_outside=['1.1.1.1/32', '2.2.2.0/24'],
        )

        clase = {
            'id': 1,
            'nombre': 'foo',
            'descripcion': 'bar',
            'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24'],
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_get.assert_called_once_with(1)
        mock_save.assert_called_once()
        assert ret.nombre == 'foo'
        assert ret.descripcion == 'bar'

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_sin_cambios(self, mock_get, mock_save):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que no
        tenga cambios
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='foo',
            descripcion='bar',
            subredes_outside=['1.1.1.1/32', '2.2.2.0/24'],
        )
        clase = {
            'id': 1,
            'nombre': 'foo',
            'descripcion': 'bar',
            'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24'],
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_get.assert_called_once_with(1)
        mock_save.assert_called_once()
        assert ret.nombre == 'foo'
        assert ret.descripcion == 'bar'

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'agregar_subred')
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_nueva_subred(self, mock_get, mock_save,
                                                mock_agregar):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga nuevas subredes
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='foo',
            descripcion='bar',
            subredes_outside=['1.1.1.1/32', '2.2.2.0/24'],
        )
        clase = {
            'id': 1,
            'nombre': 'foo',
            'descripcion': 'bar',
            'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24', '3.3.0.0/20'],
            'subredes_inside': ['4.4.4.4/32'],
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_agregar.assert_has_calls([
            call('3.3.0.0/20', netcop.ClaseTrafico.OUTSIDE),
            call('4.4.4.4/32', netcop.ClaseTrafico.INSIDE),
        ])
        assert '3.3.0.0/20' in ret.subredes_outside
        assert '4.4.4.4/32' in ret.subredes_inside

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'agregar_puerto')
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_nuevo_puerto(self, mock_get, mock_save,
                                                mock_agregar):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga nuevos puertos
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='foo',
            descripcion='bar',
            puertos_outside=[80],
        )
        clase = {
            'id': 1,
            'nombre': 'foo',
            'descripcion': 'bar',
            'puertos_outside': [443, 80],
            'puertos_inside': [1024]
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_agregar.assert_has_calls([
            call(443, netcop.ClaseTrafico.OUTSIDE),
            call(1024, netcop.ClaseTrafico.INSIDE),
        ])
        assert 443 in ret.puertos_outside
        assert 80 in ret.puertos_outside
        assert 1024 in ret.puertos_inside

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'quitar_subred')
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_eliminar_subred(self, mock_get, mock_save,
                                                   mock_quitar):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga menos subredes
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='foo',
            descripcion='bar',
            subredes_outside=['1.1.1.1/32', '2.2.2.0/24', '3.3.0.0/20'],
            subredes_inside=['4.4.4.4/32'],
        )
        clase = {
            'id': 1,
            'nombre': 'foo',
            'descripcion': 'bar',
            'subredes_outside': ['1.1.1.1/32', '2.2.2.0/24'],
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_quitar.assert_has_calls([
            call('3.3.0.0/20', netcop.ClaseTrafico.OUTSIDE),
            call('4.4.4.4/32', netcop.ClaseTrafico.INSIDE),
        ])
        assert '3.3.0.0/20' not in ret.subredes_outside
        assert ret.subredes_inside is None

    @unittest.skip("Adaptar a peewee")
    @patch.object(netcop.ClaseTrafico, 'quitar_puerto')
    @patch.object(netcop.ClaseTrafico, 'save')
    @patch.object(netcop.ClaseTrafico, 'get')
    def test_aplicar_actualizacion_eliminar_puerto(self, mock_get, mock_save,
                                                   mock_quitar):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga menos puertos
        '''
        # preparo datos
        mock_get.return_value = netcop.ClaseTrafico(
            id=1,
            nombre='foo',
            descripcion='bar',
            puertos_outside=[443, 80],
            puertos_inside=[1024]
        )
        clase = {
            'id': 1,
            'nombre': 'foo',
            'descripcion': 'bar',
            'puertos_outside': [80],
        }
        # llamo metodo a probar
        ret = self.actualizador.aplicar_actualizacion(clase)
        # verifico que todo este bien
        mock_quitar.assert_has_calls([
            call(443, netcop.ClaseTrafico.OUTSIDE),
            call(1024, netcop.ClaseTrafico.INSIDE),
        ])
        assert 443 not in ret.puertos_outside
        assert 80 in ret.puertos_outside
        assert ret.puertos_inside is None

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


if __name__ == '__main__':
    unittest.main()
