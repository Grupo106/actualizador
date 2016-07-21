# -*- coding: utf-8 -*-
'''
Pruebas del modulo actualizador.

Se prueban todos los metodos de la clase ´Actualizador´
'''
import netcop
import unittest
from mock import patch, mock_open


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
