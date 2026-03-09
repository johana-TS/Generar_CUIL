import re

def normalizar_dni(dni_raw) -> str:
    """Extrae solo los números del DNI y descarta caracteres especiales (puntos, guiones). Retorna el DNI de 8 dígitos completando con ceros si es necesario."""
    if dni_raw is None:
        return ""
        
    dni_str = str(dni_raw)
    
    # Quitar puntos, comas, espacios, etc.
    dni_limpio = re.sub(r'\D', '', dni_str)
    
    # Rellenar con ceros a la izquierda hasta llegar a 8 caracteres
    if dni_limpio:
        return dni_limpio.zfill(8)
        
    return ""

def normalizar_sexo(sexo_raw: str) -> str:
    """
    Normaliza distintas entradas de sexo a un formato estándar de un solo caracter ('M', 'F', 'I').
    """
    if not sexo_raw or not isinstance(sexo_raw, str):
        return "I" # Indefinido por defecto
        
    s = sexo_raw.strip().upper()
    
    if s in ["M", "MASCULINO", "VARON", "HOMBRE"]:
        return "M"
    elif s in ["F", "FEMENINO", "MUJER"]:
        return "F"
    else:
        return "I"
