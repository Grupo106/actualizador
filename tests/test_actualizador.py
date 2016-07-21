import unittest
import netcop


class TestActualizador(unittest.TestCase):

    def setUp(self):
        self.actualizador = netcop.Actualizador()

    def test_hay_actualizacion(self):
        self.assertTrue(self.actualizador.hay_actualizacion())


if __name__ == '__main__':
    unittest.main()
