from pydantic import BaseModel, Field, field_validator
from typing import Optional

class PersonaInput(BaseModel):
    nombre: str
    apellido: str
    nro_documento: int = Field(..., alias="dni")
    fecha_nacimiento: Optional[str] = None
    sexo: str
    
    @field_validator('sexo')
    @classmethod
    def sexo_valid(cls, v: str) -> str:
        s = v.strip().upper()
        
        # Validaciones comunes
        if s in ["M", "MASCULINO", "VARON", "HOMBRE"]:
            return "M"
        elif s in ["F", "FEMENINO", "MUJER"]:
            return "F"
        else:
            return "I" # Indefinido o Empresa

class CUILOutput(BaseModel):
    cuil: str
    prefijo: int
    dni: str
    digito: int

class RespuestaAPI(BaseModel):
    success: bool
    data: Optional[CUILOutput] = None
    error: Optional[str] = None
    codigo: int
