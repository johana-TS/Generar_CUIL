# Proyecto CUIL API

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Descripción
Proyecto en Python para procesar, calcular, validar y normalizar datos (e.g. CUIL) con una arquitectura modular. Preparado para futura integración y exposición mediante API.

## Estructura
- `src/`: Lógica de negocio core (cálculo, procesamiento, utilidades).
- `api/`: Definiciones y esquemas para la API.
- `data/`: Datos de entrada y salida.
- `tests/`: Pruebas automatizadas.

## Instalación

### Windows
Ejecuta el script de configuración que creará el entorno virtual, lo activará e instalará las dependencias necesarias:
```powershell
.\scripts\setup.ps1
```

### Linux/macOS
Ejecuta el script de configuración:
```bash
bash scripts/setup.sh
```

Opcionalmente, puedes configurar todo manualmente:
```bash
python -m venv .venv
# Activar entorno (Windows: .venv\Scripts\activate, Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
```

## Uso Básico
Ejecutar la aplicación principal:
```bash
python main.py
```

## Contribuciones
1. Haz un fork del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commits (`git commit -m 'Agregar nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.
