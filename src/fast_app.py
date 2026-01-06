"""This module handle FastAPI inst."""
import json
from typing import Any, Dict, List, Union

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.json_validator import JsonValidator


app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Render json validator."""
    return open("src/static/index.html", "rb").read()

@app.post("/upload/")
async def upload_json(file: UploadFile = File(...)) -> Dict[str, Union[str, List, Any]]:
    """Upload json file endppoint."""
    try:
        content = await file.read()
        content = content.decode("UTF-8", errors="replace")

        json_data = json.loads(content)

        # Validamos el JSON
        validator = JsonValidator(json_report=json_data)
        validator.set_json()
        validator.validate_json_name(name=file.filename)
        validator.validate_json()

        errors = validator.get_errors()

        error_list = []
        for error in errors:
            error_list.append({
                "type_error": error.get("type_error", "Desconocido"),
                "error": error.get("error", "Sin mensaje"),
                "source": error.get("source", "Objeto no encontrado.")
            })

        error_list.extend(
            {
                "type_error": "Decodificación",
                "error": f"Caracter encontrado: '{char}' en linea '{ind}'",
            }
            for ind, char in enumerate(content)
            if char == "�")

        formatted_json = json.dumps(json_data, indent=4)

        return {"json_data": formatted_json, "errors": error_list}

    except json.JSONDecodeError as e:
        return {"Error": f"Error al cargar el archivo: {str(e)}"}

    except Exception as exc:
        return {"Error": f"Error al cargar el archivo: {str(exc)}"}
