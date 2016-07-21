# -*- coding: utf-8 -*-
'''
Pruebas del modulo actualizador.

Se prueban todos los metodos de la clase ´Actualizador´
'''
import netcop
import unittest
from mock import patch, mock_open, Mock


class ActualizadorTests(unittest.TestCase):

    def setUp(self):
        self.actualizador = netcop.Actualizador()

    def test_hay_actualizacion(self):
        '''
        Prueba que el metodo hay_actualizacion devuelva verdadero cuando
        la ultima version aplicada sea distinta a la ultima version disponible.
        '''
        # preparo datos
        self.actualizador.version_actual = 'a'
        self.actualizador.version_disponible = 'b'
        # llamo metodo a probar
        assert self.actualizador.hay_actualizacion()
        
        # preparo datos
        self.actualizador.version_actual = 'b'
        self.actualizador.version_disponible = 'b'
        # llamo metodo a probar
        assert not self.actualizador.hay_actualizacion()

    @patch('netcop.actualizador.open')
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
    @patch('netcop.actualizador.open')
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

    @patch('netcop.actualizador.open')
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
    @patch('netcop.actualizador.open')
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
        ret = self.actualizador.actualizar()
        # verifico que todo este bien
        mock_descargar.assert_called_once()
        mock_aplicar.assert_called()
        assert mock_aplicar.call_count == 2
        assert self.actualizador.version_actual == 'b'
        assert ret

    def test_aplicar_actualizacion_nueva(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase inexistente
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien

    def test_aplicar_actualizacion_deshabilitar(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase que se deshabilito
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien

    def test_aplicar_actualizacion_sin_cambios(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que no
        tenga cambios
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien

    def test_aplicar_actualizacion_nueva_subred(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga nuevas subredes
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien

    def test_aplicar_actualizacion_nuevo_puerto(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga nuevos puertos
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien

    def test_aplicar_actualizacion_eliminar_subred(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga menos subredes
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien

    def test_aplicar_actualizacion_eliminar_puerto(self):
        '''
        Prueba el metodo aplicar_actualizacion con una clase existente que
        tenga menos puertos
        '''
        # preparo datos
        # llamo metodo a probar
        # verifico que todo este bien
