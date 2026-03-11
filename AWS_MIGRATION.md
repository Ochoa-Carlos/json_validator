# Migración a AWS — Plan de Onboarding

> **NOTA PARA CLAUDE CODE:** Este archivo es la fuente de verdad del proyecto de migración a AWS.
> Al iniciar una nueva sesión, lee este archivo para retomar el contexto exacto.
> Actualiza la sección "Estado actual" cada vez que se complete un paso.

## Objetivo
Migrar json_validator a AWS aprovechando el Free Tier con fines educativos.
Render se mantiene en paralelo como producción.

---

## Estado actual

**Fase activa:** Fase 0 — Setup de AWS
**Último paso completado:** Ninguno (planificación recién terminada)
**Próximo paso:** 0.1 Crear cuenta AWS
**Fecha de inicio:** 2026-03-10
**Issues en GitHub:** #61 a #84
**Milestones:** https://github.com/Ochoa-Carlos/json_validator/milestones

### Progreso por fase

| Fase | Estado | Issues |
|------|--------|--------|
| Fase 0: Setup AWS | `PENDIENTE` | #61, #62, #63, #64, #65 |
| Fase 1: Preparar código | `PENDIENTE` | #66, #67, #68, #69 |
| Fase 2: Frontend S3 + CloudFront | `PENDIENTE` | #70, #71, #72, #73, #74 |
| Fase 3: Backend EC2 | `PENDIENTE` | #75, #76, #77, #78, #79, #80 |
| Fase 4: CI/CD | `PENDIENTE` | #81, #82, #83, #84 |

### Checklist detallado

- [ ] 0.1 Crear cuenta AWS (#61)
- [ ] 0.2 Activar MFA en cuenta root (#62)
- [ ] 0.3 Crear usuario IAM para uso diario (#63)
- [ ] 0.4 Instalar y configurar AWS CLI (#64)
- [ ] 0.5 Configurar alertas de billing (#65)
- [ ] 1.1 Agregar CORS a FastAPI (#66)
- [ ] 1.2 Hacer URL de la API configurable en el frontend (#67)
- [ ] 1.3 Probar frontend y backend desacoplados localmente (#68)
- [ ] 1.4 Crear requirements-prod.txt (#69)
- [ ] 2.1 Crear bucket S3 para hosting estático (#70)
- [ ] 2.2 Subir archivos del frontend a S3 (#71)
- [ ] 2.3 Configurar hosting estático en S3 (#72)
- [ ] 2.4 Configurar bucket policy para lectura pública (#73)
- [ ] 2.5 Crear distribución CloudFront (#74)
- [ ] 3.1 Crear Key Pair para SSH (#75)
- [ ] 3.2 Crear Security Group / firewall (#76)
- [ ] 3.3 Lanzar instancia EC2 t2.micro (#77)
- [ ] 3.4 Asignar Elastic IP (#78)
- [ ] 3.5 Instalar Docker en EC2 y desplegar contenedor (#79)
- [ ] 3.6 Conectar frontend (CloudFront) con backend (EC2) (#80)
- [ ] 4.1 Crear usuario IAM para CI/CD (#81)
- [ ] 4.2 Configurar GitHub Secrets (#82)
- [ ] 4.3 Pipeline de deploy frontend (#83)
- [ ] 4.4 Pipeline de deploy backend (#84)

### Recursos AWS creados
_(Se actualiza conforme se crean)_
- **S3 Bucket:** pendiente
- **CloudFront Distribution ID:** pendiente
- **CloudFront URL:** pendiente
- **EC2 Instance ID:** pendiente
- **Elastic IP:** pendiente
- **Key Pair:** pendiente
- **Security Group:** pendiente

### Decisiones tomadas
- Opción B: S3 + CloudFront (frontend) + EC2 t2.micro (backend)
- Mismo repo (no se clona). Render sigue en paralelo.
- Sin dominio propio, se usan URLs generadas por AWS.
- Post mes 11: migrar a serverless (Lambda) para $0 permanente.
- Usuario no tiene experiencia con firewalls → explicar Security Groups en detalle.

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
