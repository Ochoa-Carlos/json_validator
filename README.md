# Validador de JSONs Mensuales para Controles Volumétricos según SAT

## Descripción General

Validador de JSON's diseñado para verificar el cumplimiento de los controles volumétricos según las reglas establecidas por el **SAT (Servicio de Administración Tributaria)**.

## Funcionalidades

- Validación de estructura de JSON.
- Verificación de campos obligatorios.
- Validación de formatos y expresiones regulares.
- Validación de valores mínimos y máximos.
- Registro de errores con mensajes detallados.
- Validación de características específicas por tipo de usuario.

---



## 🚀 Cómo Levantar la Aplicación con Docker

Puedes ejecutar la aplicación usando **Docker Compose** o **Docker**.
---

### 1. Docker Compose

```bash
docker-compose up --build && docker compose up -d
```

### 2. Docker

```bash
docker build -t json-validator .
docker run -p 3001:3001 json-validator
```