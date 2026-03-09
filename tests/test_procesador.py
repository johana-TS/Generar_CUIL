import unittest
import sys
import os
import tempfile
import json
import csv
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from calculador.core import CalculadorCUIL
from procesador.archivos import ProcesadorLotes

class TestProcesadorLotes(unittest.TestCase):
    def setUp(self):
        self.calculador = CalculadorCUIL()
        # Usamos un directorio temporal para no dejar basura o modificar docs de git
        self.temp_dir = tempfile.TemporaryDirectory()
        self.procesador = ProcesadorLotes(self.calculador, directorio_salida=self.temp_dir.name)

        # Datos de prueba
        self.personas_mock = [
            {"dni": "12345678", "sexo": "M"}, # Éxito
            {"dni": 12345678, "sexo": "F"},   # Éxito (numérico)
            {"dni": -10, "sexo": "M"},        # Error de validación (negativo)
            {"dni": "99999999", "sexo": "X"}, # Error validación (sexo)
            {"dni": None, "sexo": "M"}        # Error (falta DNI o None)
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_procesar_lista_en_memoria(self):
        """Test procesando directamente la lista de diccionarios"""
        resumen = self.procesador.procesar_lista(self.personas_mock, nombre_lote="test_memoria", formato_salida="json")
        
        self.assertEqual(resumen["total"], 5)
        self.assertEqual(resumen["exitosos"], 2)
        self.assertEqual(resumen["fallidos"], 3)
        self.assertTrue(os.path.exists(resumen["archivo_salida"]))
        self.assertTrue(os.path.exists(resumen["archivo_errores"]))

        # Verificar contenido de éxito
        with open(resumen["archivo_salida"], 'r') as f:
            datos = json.load(f)
            self.assertEqual(len(datos), 2)
            self.assertEqual(datos[0]["cuil"], "20-12345678-6")
            
    def test_procesar_archivo_csv(self):
        """Test procesando un archivo CSV de entrada"""
        ruta_csv = os.path.join(self.temp_dir.name, "entrada.csv")
        
        # Crear CSV temporal usando Pandas
        df = pd.DataFrame(self.personas_mock)
        df.to_csv(ruta_csv, index=False)
        
        resumen = self.procesador.procesar_archivo(ruta_csv, formato_salida="csv")
        
        self.assertEqual(resumen["total"], 5)
        self.assertEqual(resumen["exitosos"], 2)
        
        # Verificar export en CSV
        with open(resumen["archivo_salida"], 'r') as f:
            reader = csv.DictReader(f)
            filas = list(reader)
            self.assertEqual(len(filas), 2)
            self.assertEqual(filas[0]["cuil"], "20-12345678-6")

if __name__ == "__main__":
    unittest.main(verbosity=2)
