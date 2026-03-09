import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from utils.validadores import validar_formato_dni, validar_formato_cuil
from utils.normalizadores import normalizar_dni, normalizar_sexo

class TestUtilidades(unittest.TestCase):
    
    def test_validar_formato_dni(self):
        self.assertTrue(validar_formato_dni("12345678"))
        self.assertTrue(validar_formato_dni(123456))
        self.assertFalse(validar_formato_dni("123456789")) # más de 8
        self.assertFalse(validar_formato_dni("12.345"))     # no numérico
        self.assertFalse(validar_formato_dni("12abc"))      # alfanumérico
        
    def test_validar_formato_cuil(self):
        self.assertTrue(validar_formato_cuil("20-12345678-6"))
        self.assertFalse(validar_formato_cuil("20123456786"))
        self.assertFalse(validar_formato_cuil("20-1234567-6"))
        
    def test_normalizar_dni(self):
        self.assertEqual(normalizar_dni("12.345.678"), "12345678")
        self.assertEqual(normalizar_dni(" 1 2 3 "), "00000123")
        self.assertEqual(normalizar_dni("ab12cd"), "00000012")
        self.assertEqual(normalizar_dni(None), "")
        
    def test_normalizar_sexo(self):
        self.assertEqual(normalizar_sexo("m"), "M")
        self.assertEqual(normalizar_sexo("Masculino"), "M")
        self.assertEqual(normalizar_sexo(" Mujer "), "F")
        self.assertEqual(normalizar_sexo("Desconocido"), "I")
        self.assertEqual(normalizar_sexo(None), "I")

if __name__ == '__main__':
    unittest.main(verbosity=2)
