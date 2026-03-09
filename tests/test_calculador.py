import unittest
import sys
import os

# Agregamos src al PYTHONPATH para que encuentre los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from calculador.core import CalculadorCUIL

class TestCalculadorCUIL(unittest.TestCase):
    def setUp(self):
        self.calculador = CalculadorCUIL()

    def test_calculo_normal_masculino(self):
        """Test genérico de DNI con prefijo 20"""
        resultado = self.calculador.calcular(12345678, "M")
        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["data"]["cuil"], "20-12345678-6")
        self.assertEqual(resultado["data"]["prefijo"], 20)
        self.assertEqual(resultado["data"]["digito"], 6)

    def test_calculo_normal_femenino(self):
        """Test genérico de DNI con prefijo 27"""
        resultado = self.calculador.calcular(12345678, "F")
        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["data"]["cuil"], "27-12345678-0")
        self.assertEqual(resultado["data"]["prefijo"], 27)
        self.assertEqual(resultado["data"]["digito"], 0)

    def test_calculo_overflow_masculino(self):
        """Test de colisión para forzar el prefijo 23 y dígito 9 en masculino"""
        # Para el DNI 11111118 y sexo M (20), el cálculo de la suma ponderada genera resto 1
        resultado = self.calculador.calcular(11111118, "M")
        self.assertTrue(resultado["success"], f"Fallo al calcular: {resultado.get('error')}")
        self.assertEqual(resultado["data"]["cuil"], "23-11111118-9")
        self.assertEqual(resultado["data"]["prefijo"], 23)
        self.assertEqual(resultado["data"]["digito"], 9)

    def test_validacion_errores(self):
        """Test de las validaciones de error en los tipos de datos"""
        res_negativo = self.calculador.calcular(-10, "M")
        self.assertFalse(res_negativo["success"])
        self.assertEqual(res_negativo["codigo"], 1)

        res_sexo_invalido = self.calculador.calcular(12345678, "X")
        self.assertFalse(res_sexo_invalido["success"])
        self.assertEqual(res_sexo_invalido["codigo"], 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
