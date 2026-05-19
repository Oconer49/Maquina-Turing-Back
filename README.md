# Backend — Simulador de Máquinas de Turing

API REST en **FastAPI** que ejecuta máquinas de Turing deterministas de una cinta. El frontend consume estos endpoints para mostrar la cinta, los pasos y la tabla δ.

## Requisitos

| Herramienta | Versión |
|-------------|---------|
| Python | 3.11 o superior |
| pip | Incluido con Python |

Instala Python desde https://www.python.org/downloads/ y marca **“Add python.exe to PATH”**.

## Instalar dependencias

### Opción A — Windows (recomendada)

Desde la carpeta `backend`:

```powershell
.\setup-backend.bat
```

Ese script:

1. Busca Python en el sistema.
2. Crea el entorno virtual `.venv`.
3. Ejecuta `pip install -r requirements.txt`.

### Opción B — Manual

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Qué instala `requirements.txt`

| Paquete | Para qué sirve |
|---------|----------------|
| **fastapi** | Framework web y rutas `/api/v1/...` |
| **uvicorn** | Servidor ASGI que ejecuta la app |
| **pydantic** | Validación de JSON (máquinas, simulaciones) |
| **pytest** / **httpx** | Pruebas automáticas de la API |

## Ejecutar el servidor

```powershell
.\start-backend.bat
```

O manualmente (con el venv activado):

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **API:** http://localhost:8000  
- **Documentación interactiva:** http://localhost:8000/docs  
- **Health check:** http://localhost:8000/api/v1/health  

## Variables de entorno

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `CORS_ORIGINS` | URLs del frontend separadas por coma | `http://localhost:5173` |
| `PORT` | Puerto (Render lo define solo) | `8000` en local |

Ejemplo producción:

```
CORS_ORIGINS=https://tu-app.onrender.com
```

## Pruebas

```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

## Estructura del código

```
backend/
├── app/
│   ├── main.py              # App FastAPI, CORS, monta rutas
│   ├── config.py            # Límites de pasos, CORS, ventana de cinta
│   ├── api/v1/simulation.py # Endpoints REST
│   ├── core/
│   │   ├── tape.py          # Cinta infinita (dict + cabeza)
│   │   ├── turing_engine.py # Motor: step, run, reset
│   │   ├── validator.py     # Valida máquina y cadena de entrada
│   │   └── result_explainer.py  # Mensajes de aceptación/rechazo
│   ├── models/              # Esquemas Pydantic
│   ├── services/
│   │   ├── preset_loader.py # Lee JSON de app/presets/
│   │   └── simulation_store.py  # Sesiones en memoria (UUID → motor)
│   └── presets/*.json       # Máquinas predefinidas
├── requirements.txt
├── setup-backend.bat
└── start-backend.bat
```

## Cómo funciona el código

### 1. Arranque (`main.py`)

- Crea la app FastAPI.
- Aplica **CORS** para que el frontend en otro puerto pueda llamar la API.
- Registra el router bajo el prefijo `/api/v1`.

### 2. Máquinas preset (`preset_loader.py`)

- Al iniciar, lee los archivos `.json` en `app/presets/`.
- Cada JSON define: estados, alfabetos, blanco, estados finales y lista de transiciones δ.
- `GET /machines` devuelve el listado; `GET /machines/{id}` la definición completa.

### 3. Crear simulación (`simulation.py` → `TuringEngine`)

1. El cliente envía `machine_id` + `input` (cadena).
2. **Validator** comprueba que la máquina sea coherente y que cada símbolo de la cadena esté en Σ.
3. Se instancia **TuringEngine** con la cinta inicial cargada con la entrada.
4. **SimulationStore** guarda el motor en memoria y devuelve un `simulation_id` (UUID).

### 4. Un paso de simulación (`turing_engine.py`)

Flujo de `step()`:

1. Si ya no está `RUNNING`, devuelve el snapshot actual.
2. **Lee** el símbolo bajo la cabeza (`tape.read()`).
3. Busca δ(estado, símbolo) en un mapa precalculado.
4. Si no hay transición → **REJECTED** (`no_transition`).
5. Si hay transición → escribe, cambia de estado, mueve la cabeza (L/R).
6. Si el nuevo estado es de aceptación o rechazo → actualiza el status.
7. **snapshot()** arma el JSON: cinta (ventana alrededor de la cabeza), paso, estado, última δ, mensaje pedagógico.

### 5. La cinta (`tape.py`)

- No es un array fijo: usa un `dict` índice → símbolo (cinta infinita hacia ambos lados).
- Celdas no escritas se tratan como **blanco** (`_`, mostrado como ⊔ en el frontend).
- `window(radius)` recorta un tramo para enviar al cliente sin mandar toda la cinta.

### 6. Sesiones en memoria (`simulation_store.py`)

- Cada simulación vive en un diccionario `{ simulation_id: TuringEngine }`.
- Al reiniciar el servidor se pierden las sesiones (diseño educativo, sin base de datos).

### 7. Endpoints principales

| Método | Ruta | Acción |
|--------|------|--------|
| GET | `/api/v1/machines` | Lista máquinas |
| GET | `/api/v1/machines/{id}` | Detalle de una máquina |
| POST | `/api/v1/simulations` | Crea simulación |
| POST | `/api/v1/simulations/{id}/step` | Un paso |
| POST | `/api/v1/simulations/{id}/run` | Varios pasos de golpe |
| POST | `/api/v1/simulations/{id}/reset` | Vuelve al inicio |
| GET | `/api/v1/health` | Estado del servicio |

## Despliegue en Render

1. https://dashboard.render.com → **New** → **Blueprint** o **Web Service** → repo **Maquina-Turing-Back**
2. Usa `render.yaml` del repo o Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Variable `CORS_ORIGINS` = URL del Static Site del frontend (sin `/` al final)
