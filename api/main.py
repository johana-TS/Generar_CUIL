import sys
import os
import uuid
import shutil
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from calculador.core import CalculadorCUIL
from procesador.archivos import ProcesadorLotes
from api.schemas import PersonaInput, RespuestaAPI, CUILOutput

app = FastAPI(
    title="API Sistema CUIL",
    description="API para el cálculo individual y procesamiento por lotes de números CUIL.",
    version="1.0.0"
)

# Instancias compartidas
calculador_global = CalculadorCUIL()
# Simulador de DB en memoria para trackear el estado de los lotes asíncronos
# Estructura: {"id_lote": {"estado": "procesando" | "completado" | "error", "resultado": dict}}
estados_lotes: Dict[str, Dict[str, Any]] = {}

@app.post("/calcular", response_model=RespuestaAPI)
def calcular_individual(persona: PersonaInput):
    """
    Recibe los datos de una persona y retorna su CUIL.
    """
    try:
        resultado = calculador_global.calcular(persona.nro_documento, persona.sexo)
        
        if resultado["success"]:
            data_out = CUILOutput(
                cuil=resultado["data"]["cuil"],
                prefijo=resultado["data"]["prefijo"],
                dni=resultado["data"]["dni"],
                digito=resultado["data"]["digito"]
            )
            return RespuestaAPI(success=True, data=data_out, codigo=resultado["codigo"])
        else:
            return RespuestaAPI(success=False, error=resultado["error"], codigo=resultado["codigo"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _tarea_procesamiento_lote(id_lote: str, file_path: str, output_dir: str):
    """Tarea asíncrona ("background") para procesar el archivo CSV/JSON guardado."""
    try:
        procesador = ProcesadorLotes(calculador_global, directorio_salida=output_dir)
        # Procesar
        resumen = procesador.procesar_archivo(file_path, formato_salida="json")
        # Actualizar estado
        estados_lotes[id_lote] = {
            "estado": "completado",
            "resultado": resumen
        }
    except Exception as e:
        estados_lotes[id_lote] = {
            "estado": "error",
            "resultado": {"error": str(e)}
        }

@app.post("/procesar-lote")
async def procesar_lote_endpoint(background_tasks: BackgroundTasks, archivo: UploadFile = File(...)):
    """
    Sube un archivo (CSV/Excel/JSON) para iniciar un proceso Batch Asíncrono.
    Retorna un ID de lote para consultar el estado.
    """
    # Validar extensión
    ext = os.path.splitext(archivo.filename)[1].lower()
    if ext not in ['.csv', '.json', '.xls', '.xlsx']:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Debe ser CSV, JSON o Excel.")
        
    id_lote = str(uuid.uuid4())
    input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'input'))
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'output'))
    
    os.makedirs(input_dir, exist_ok=True)
    file_path = os.path.join(input_dir, f"{id_lote}{ext}")
    
    # Escribir el archivo recibido a disco
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)
        
    # Registrar en nuestra "BD en memoria"
    estados_lotes[id_lote] = {"estado": "procesando", "resultado": None}
    
    # Enviar al Background
    background_tasks.add_task(_tarea_procesamiento_lote, id_lote, file_path, output_dir)
    
    return {
        "success": True,
        "mensaje": "El archivo fue subido y su procesamiento comenzó.",
        "id_lote": id_lote
    }

@app.get("/estado/{id_lote}")
def consultar_estado_lote(id_lote: str):
    """
    Consulta el estado de un lote asíncrono previamente enviado.
    """
    estado_data = estados_lotes.get(id_lote)
    
    if not estado_data:
        raise HTTPException(status_code=404, detail="ID de lote no encontrado.")
        
    return estado_data
