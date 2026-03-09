import os
import sys
import argparse
import logging
from pprint import pprint

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from calculador.core import CalculadorCUIL
from procesador.archivos import ProcesadorLotes

def configurar_logging(verbose: bool):
    """Configura el nivel de logging basado en el flag verbose."""
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def procesar_cli():
    parser = argparse.ArgumentParser(
        description="CLI para el procesamiento por lotes de CUILs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Opciones requeridas
    parser.add_argument("--input", required=True, help="Archivo de entrada (requerido) [CSV, Excel, JSON].")
    
    # Opciones opcionales
    parser.add_argument("--output", help="Prefijo/Nombre del archivo de salida (opcional).")
    parser.add_argument("--formato", choices=["json", "csv"], default="json", help="Formato de salida (default: json).")
    parser.add_argument("--delimitador", default=",", help="Delimitador CSV (default: ,).")
    parser.add_argument("--dry-run", type=int, metavar="N", help="Procesar solo N registros para prueba.")
    parser.add_argument("--verbose", action="store_true", help="Mostrar información detallada.")
    parser.add_argument("--checkpoint", type=int, default=100, metavar="CADA", help="Guardar checkpoint cada X registros (default: 100). [Nota: TODO en futura iteración batch]")
    parser.add_argument("--no-bar", action="store_true", help="Ocultar barra de progreso.")

    args = parser.parse_args()
    return args

def main():
    args = procesar_cli()
    configurar_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    logger.info("Iniciando Proyecto CUIL API - Modo CLI")
    
    # Instanciar núcleo
    calculador = CalculadorCUIL()
    
    # Determinar directorio base
    # Si manda --output usamos ese nombre (o ruta)
    if args.output:
        dir_salida = os.path.dirname(args.output) or "data/output"
        nombre_lote = os.path.basename(args.output)
        # Quitar extensión si fue provista, el procesador la pone
        nombre_lote = os.path.splitext(nombre_lote)[0]
    else:
        dir_salida = "data/output"
        # Usa el mismo nombre del input
        nombre_lote = os.path.splitext(os.path.basename(args.input))[0] + "_out"

    logger.debug(f"Directorio de salida: {dir_salida}")
    logger.debug(f"Nombre del lote: {nombre_lote}")

    procesador = ProcesadorLotes(calculador, directorio_salida=dir_salida)
    
    try:
        import pandas as pd
        
        logger.info(f"Leyendo archivo de entrada: {args.input}")
        ext = os.path.splitext(args.input)[1].lower()
        
        # Lectura inicial según extensión
        if ext == '.csv':
            df = pd.read_csv(args.input, sep=args.delimitador)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(args.input)
        elif ext == '.json':
            df = pd.read_json(args.input)
        else:
            logger.error(f"Formato de archivo no soportado: {ext}")
            sys.exit(1)
            
        columnas = [str(c).lower() for c in df.columns]
        df.columns = columnas
        
        if 'dni' not in columnas or 'sexo' not in columnas:
            logger.error("El archivo debe contener las columnas 'dni' y 'sexo'")
            sys.exit(1)
            
        # Aplicar dry-run si fue solicitado
        if args.dry_run:
            logger.info(f"Modo DRY-RUN activo. Procesando solo los primeros {args.dry_run} registros.")
            df = df.head(args.dry_run)
            
        personas = df[['dni', 'sexo']].to_dict('records')
        logger.info(f"Total de registros a procesar: {len(personas)}")
        
        # Procesar
        # Ocultar barra si --no-bar
        # Modifico dinámicamente el comportamiento de tqdm en ProcesadorLotes (monkey-patching temporal)
        if args.no_bar:
            import procesador.archivos as pa
            pa.tqdm = lambda x, **kwargs: x
            logger.debug("Barra de progreso desactivada.")
            
        resumen = procesador.procesar_lista(
            personas, 
            nombre_lote=nombre_lote, 
            formato_salida=args.formato
            # TODO: Evaluar implementar `checkpoint` en read/write streams futuros si crecen los datos
        )
        
        logger.info("Procesamiento completado exitosamente.")
        print("\n=== Resumen de Ejecución ===")
        pprint(resumen)

    except Exception as e:
        logger.error(f"Error durante la ejecución: {str(e)}", exc_info=args.verbose)
        sys.exit(1)

if __name__ == "__main__":
    main()
