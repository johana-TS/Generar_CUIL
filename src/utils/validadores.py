import re

def validar_formato_dni(dni_str: str) -> bool:
    """Verifica que el DNI sea únicamente numérico y tenga como máximo 8 caracteres."""
    if not isinstance(dni_str, str):
        dni_str = str(dni_str)
    return bool(re.fullmatch(r'\d{1,8}', dni_str))

def validar_formato_cuil(cuil_str: str) -> bool:
    """Verifica si un string tiene el formato clásico de CUIL."""
    return bool(re.fullmatch(r'\d{2}-\d{8}-\d{1}', cuil_str))
