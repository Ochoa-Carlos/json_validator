from setuptools import setup

APP = ["src/main.py"]  # La ruta al archivo principal de tu aplicación
DATA_FILES = ["assets/logo_digamma.gif"]
OPTIONS = {
    "argv_emulation": True,
    "packages": ["tkinter", "json", "datetime", "typing", "functools", "sys", "traceback", "re", "typing",
                 "enum"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
