# Migración a AWS — Plan de Onboarding

## Objetivo
Migrar json_validator a AWS aprovechando el Free Tier con fines educativos.
Render se mantiene en paralelo como producción.

## Arquitectura

```
                          ┌─────────────────────┐
                          │      Usuario         │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  CloudFront (CDN)     │
                          │  d1234.cloudfront.net │
                          │  HTTPS automático     │
                          └──────────┬───────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                                       │
      ┌──────────▼───────────┐              ┌────────────▼──────────┐
      │   S3 Bucket          │              │   EC2 t2.micro        │
      │   (Frontend)         │              │   (Backend)           │
      │                      │              │                       │
      │   index.html         │   POST       │   FastAPI + Uvicorn   │
      │   indexApp.css       │──/upload/──►  │   Docker              │
      │   index.css          │              │   Puerto 3001         │
      │   logo_digamma.gif   │              │   Elastic IP          │
      └──────────────────────┘              └───────────────────────┘
                                                      │
                                              Security Group:
                                              - SSH (22): solo tu IP
                                              - TCP (3001): abierto
```

---

## Fase 0 — Setup de AWS
**Objetivo:** Cuenta AWS funcional, segura, con herramientas listas.
**Aprenderás:** IAM, MFA, AWS CLI, buenas prácticas de seguridad en la nube.

| Paso | Tarea | Detalle |
|------|-------|---------|
| 0.1 | Crear cuenta AWS | Con tarjeta de crédito. No se cobra. |
| 0.2 | Activar MFA en cuenta root | Usar app de autenticación (Google Authenticator, Authy). |
| 0.3 | Crear usuario IAM | Usuario con permisos administrativos para uso diario. Generar Access Key + Secret Key. |
| 0.4 | Instalar AWS CLI | Configurar con `aws configure` usando las keys del paso anterior. |
| 0.5 | Configurar alertas de billing | Alarma en CloudWatch a $1 y $5. **Innegociable.** |

**Verificación:** `aws sts get-caller-identity` devuelve tu usuario IAM.

---

## Fase 1 — Preparación del código
**Objetivo:** Separar frontend y backend para que funcionen independientemente.
**Aprenderás:** CORS, configuración por entorno, arquitectura desacoplada.

| Paso | Tarea | Detalle |
|------|-------|---------|
| 1.1 | Agregar CORS a FastAPI | `CORSMiddleware` permitiendo requests desde cualquier origen (luego se restringe a CloudFront). |
| 1.2 | URL de API configurable en frontend | Cambiar `/upload/` (relativa) a URL absoluta via `config.js`. |
| 1.3 | Probar localmente | FastAPI en un puerto + `index.html` abierto desde archivo. Validación debe funcionar. |
| 1.4 | Limpiar dependencias | Crear `requirements-prod.txt` sin py2app, pyinstaller. |

**Verificación:** `index.html` abierto desde explorador de archivos valida JSONs contra FastAPI en `localhost:3001`.

---

## Fase 2 — Frontend en S3 + CloudFront
**Objetivo:** Servir el frontend desde AWS.
**Aprenderás:** S3, políticas de bucket, CloudFront (CDN), caché.

| Paso | Tarea | Detalle |
|------|-------|---------|
| 2.1 | Crear bucket S3 | Nombre único global. Región: `us-east-1`. |
| 2.2 | Subir archivos del frontend | `aws s3 sync` con `index.html`, CSS y logo. |
| 2.3 | Configurar hosting estático | Activar "Static website hosting". Documento índice: `index.html`. |
| 2.4 | Política del bucket | Bucket policy para lectura pública. |
| 2.5 | Verificar acceso S3 | Acceder via URL de S3 website. |
| 2.6 | Crear distribución CloudFront | Origin: URL de S3. Obtienes URL `d1234.cloudfront.net`. |
| 2.7 | Configurar caché | Default TTL 24h. |
| 2.8 | Verificar CloudFront | Frontend carga con HTTPS automático. |

**Verificación:** URL de CloudFront muestra el frontend (validación aún no funciona).

---

## Fase 3 — Backend en EC2
**Objetivo:** Correr la API en la nube.
**Aprenderás:** EC2, Security Groups (firewall), SSH remoto, Docker en la nube, Elastic IP.

### 3A — Lanzar instancia

| Paso | Tarea | Detalle |
|------|-------|---------|
| 3.1 | Crear Key Pair | Para SSH. Guardar `.pem` con `chmod 400`. |
| 3.2 | Crear Security Group | Inbound SSH (22): solo tu IP. Inbound TCP (3001): 0.0.0.0/0. |
| 3.3 | Lanzar instancia EC2 | AMI: Amazon Linux 2023 o Ubuntu 22.04. Tipo: `t2.micro`. |
| 3.4 | Asignar Elastic IP | Gratis mientras la instancia corre. **Cobra si está apagada.** |

### 3B — Configurar servidor

| Paso | Tarea | Detalle |
|------|-------|---------|
| 3.5 | Conectar por SSH | `ssh -i key.pem ec2-user@<ELASTIC-IP>` |
| 3.6 | Instalar Docker | Según AMI elegida. |
| 3.7 | Subir proyecto | `git clone` del repo en la instancia. |
| 3.8 | Build y run | `docker build` + `docker run -d -p 3001:3001`. |
| 3.9 | Verificar API | `curl http://<ELASTIC-IP>:3001/` desde tu máquina. |

### 3C — Conectar frontend con backend

| Paso | Tarea | Detalle |
|------|-------|---------|
| 3.10 | Actualizar URL en frontend | Apuntar a `http://<ELASTIC-IP>:3001`. |
| 3.11 | Re-subir frontend a S3 | `aws s3 sync`. |
| 3.12 | Invalidar caché CloudFront | `aws cloudfront create-invalidation`. |
| 3.13 | Restringir CORS | Solo aceptar requests desde URL de CloudFront. |

**Verificación:** CloudFront → subir JSON → validación funciona end-to-end.

---

## Fase 4 — CI/CD con GitHub Actions
**Objetivo:** Deploy automático al hacer push.
**Aprenderás:** GitHub Actions, IAM programático, secrets management.

| Paso | Tarea | Detalle |
|------|-------|---------|
| 4.1 | Crear usuario IAM para CI/CD | Permisos mínimos: S3 sync + CloudFront invalidation. |
| 4.2 | Configurar GitHub Secrets | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `EC2_SSH_KEY`, `EC2_HOST`. |
| 4.3 | Pipeline frontend | On push a `main` (cambios en `src/static/`) → S3 sync + invalidar CF. |
| 4.4 | Pipeline backend | On push a `main` (cambios en `src/*.py`) → SSH a EC2 → git pull + docker rebuild. |
| 4.5 | Probar pipelines | Push cambio menor, verificar deploy automático. |

**Verificación:** Push → deploy sin intervención manual.

---

## Timeline

| Semana | Fase | Horas estimadas |
|--------|------|-----------------|
| 1 | Fase 0: Setup AWS | ~2h |
| 2 | Fase 1: Preparar código | ~3h |
| 3-4 | Fase 2: S3 + CloudFront | ~4h |
| 4-6 | Fase 3: EC2 | ~6h |
| 7-8 | Fase 4: CI/CD | ~4h |

**Total: ~19 horas ≈ 6-8 semanas a 30-90 min/día**

---

## Futuro (Post Fase 4)
- **Mes 7-10:** Migrar backend a Lambda + Function URL (Always Free)
- **Mes 11:** Apagar EC2 → $0 permanente
