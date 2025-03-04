import json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.json_validator import JsonValidator

app = FastAPI()

# Montar la carpeta 'static' para servir archivos estáticos
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Servir el archivo index.html
    return open("src/static/index.html").read()

@app.post("/upload/")
async def upload_json(file: UploadFile = File(...)):
    try:
        # Leemos el archivo JSON subido
        content = await file.read()
        json_data = json.loads(content)

        # Validamos el JSON
        validator = JsonValidator(json_report=json_data)
        validator.set_json()
        validator.validate_json()

        errors = validator.get_errors()

        # Convertimos los errores en un formato entendible
        error_list = []
        for error in errors:
            error_list.append({
                "type_error": error.get("type_error", "Desconocido"),
                "error": error.get("error", "Sin mensaje")
            })

        # Formatear el JSON para enviarlo con indentación
        formatted_json = json.dumps(json_data, indent=4)
        print("LISTA DE ERRORES", error_list)
        # Devolver el JSON formateado y los errores (si los hay)
        return {"json_data": formatted_json, "errors": error_list}

    except json.JSONDecodeError as e:
        return {"error": f"Error al cargar el archivo: {str(e)}"}
