import os
import json
import csv
import time
import pandas as pd
from typing import List, Dict, Any, Union
try:
    from tqdm import tqdm
except Exception:
    # Fallback simple si tqdm no está instalado
    tqdm = lambda x, **kwargs: x

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculador.core import CalculadorCUIL

class ProcesadorLotes:
    """Clase para procesar lotes de DNIs y generar CUILs, con exportación a archivos."""
    
    def __init__(self, calculador: CalculadorCUIL, directorio_salida: str = "data/output"):
        self.calculador = calculador
        self.directorio_salida = directorio_salida
        
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)

    def _guardar_resultados(self, resultados: List[Dict], formato: str, ruta_base: str):
        """Guarda los resultados exitosos en formato JSON o CSV."""
        if not resultados:
            return None
            
        ruta_salida = f"{ruta_base}.{formato}"
        
        if formato.lower() == 'json':
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=4, ensure_ascii=False)
        elif formato.lower() == 'csv':
            if resultados:
                claves = resultados[0].keys()
                with open(ruta_salida, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=claves)
                    writer.writeheader()
                    writer.writerows(resultados)
        else:
            raise ValueError(f"Formato no soportado: {formato}")
            
        return ruta_salida

    def _guardar_errores(self, errores: List[Dict], ruta_base: str):
        """Siempre guarda los errores en formato CSV."""
        if not errores:
            return None
            
        ruta_errores = f"{ruta_base}_errores.csv"
        claves = errores[0].keys()
        
        with open(ruta_errores, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=claves)
            writer.writeheader()
            writer.writerows(errores)
            
        return ruta_errores

    def procesar_lista(self, personas: List[Dict[str, Any]], nombre_lote: str = "batch", formato_salida: str = "json") -> Dict[str, Any]:
        """
        Procesa una lista en memoria.
        
        Args:
            personas (list): Lista de diccionarios con claves 'dni' y 'sexo'.
            nombre_lote (str): Nombre base para los archivos generados.
            formato_salida (str): 'json' o 'csv'
            
        Returns:
            dict: Resumen del procesamiento.
        """
        inicio = time.time()
        
        exitos = []
        errores = []
        
        for item in tqdm(personas, desc=f"Procesando lote '{nombre_lote}'"):
            dni = item.get('dni')
            sexo = item.get('sexo')
            
            # Intento de cálculo
            try:
                # Ojo: dni podría venir como string numérico
                dni_val = int(dni) if dni is not None else -1
                resultado = self.calculador.calcular(dni_val, sexo)
                
                if resultado['success']:
                    registro_exitoso = {
                        "dni_original": dni,
                        "sexo_original": sexo,
                        "cuil": resultado['data']['cuil'],
                        "prefijo_asignado": resultado['data']['prefijo'],
                        "digito": resultado['data']['digito']
                    }
                    exitos.append(registro_exitoso)
                else:
                    registro_error = {
                        "dni": dni,
                        "sexo": sexo,
                        "error_msj": resultado['error'],
                        "codigo_error": resultado['codigo']
                    }
                    errores.append(registro_error)
            except Exception as e:
                errores.append({
                    "dni": dni,
                    "sexo": sexo,
                    "error_msj": f"Error no controlado: {str(e)}",
                    "codigo_error": 3
                })

        # Guardado
        ruta_base = os.path.join(self.directorio_salida, nombre_lote)
        
        archivo_salida = self._guardar_resultados(exitos, formato_salida, ruta_base)
        archivo_errores = self._guardar_errores(errores, ruta_base)
            
        tiempo_total = time.time() - inicio
        
        return {
            "total": len(personas),
            "exitosos": len(exitos),
            "fallidos": len(errores),
            "archivo_salida": archivo_salida,
            "archivo_errores": archivo_errores,
            "tiempo_segundos": round(tiempo_total, 3)
        }

    def procesar_archivo(self, ruta_entrada: str, formato_salida: str = "json") -> Dict[str, Any]:
        """
        Lee un archivo (CSV, Excel o JSON), extrae la lista de personas y las procesa.
        
        Se asume que el archivo tiene las columnas/claves: 'dni' y 'sexo'.
        """
        if not os.path.exists(ruta_entrada):
            raise FileNotFoundError(f"El archivo {ruta_entrada} no existe.")
            
        nombre_base = os.path.splitext(os.path.basename(ruta_entrada))[0]
        ext = os.path.splitext(ruta_entrada)[1].lower()
        
        if ext == '.csv':
            df = pd.read_csv(ruta_entrada)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(ruta_entrada)
        elif ext == '.json':
            df = pd.read_json(ruta_entrada)
        else:
            raise ValueError(f"Formato de archivo de entrada no soportado: {ext}")
            
        # Convertir dataframe a lista de diccionarios
        # Aseguramos que 'dni' y 'sexo' existen
        columnas = [str(c).lower() for c in df.columns]
        df.columns = columnas
        
        if 'dni' not in columnas or 'sexo' not in columnas:
            raise KeyError("El archivo de entrada debe contener las columnas 'dni' y 'sexo'.")
            
        personas = df[['dni', 'sexo']].to_dict('records')
        
        return self.procesar_lista(personas, nombre_lote=nombre_base, formato_salida=formato_salida)
