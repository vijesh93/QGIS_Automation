# QGIS_Automation

This repository automates QGIS tasks inside a Docker container. It contains Dockerfiles and Compose overrides for development and production workflows.

**Purpose**
This project automates recurring GIS workflows using QGIS in a containerized environment. The first automated task implemented by the project is:
- Connect to a database, fetch a specific table, and export it as a layer in QGIS (e.g. GeoPackage, Shapefile, or PostGIS layer export).  
This automation is intended to make repeated exports reproducible, schedulable, and portable across environments.

**Prerequisites**
- **Docker**: Desktop or Engine installed and running.
- **docker-compose**: the v1 `docker-compose` CLI or the `docker compose` plugin.
- Optional: `make` and PowerShell for provided helpers.

**Quick Start (Dev)**
- Copy `.env.example` to `.env` and fill any values you need (this file is gitignored):
  - `IMAGE_NAME` and `IMAGE_TAG` control image tagging.
- Build and run dev (mounts source and keeps container open for debugging):
  ```powershell
  docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml build
  docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d
  ```
- Enter the running container (replace service name if different):
  ```powershell
  docker-compose exec qgis-app bash
  ```

**Build & Run (Prod)**
- Prod runs the baked image (no source mount). Set `IMAGE_NAME`/`IMAGE_TAG` locally or in CI to control tags.
  ```powershell
  docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml build
  docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d
  ```

**Image Naming**
- The base `docker-compose.yaml` contains an `image:` entry that is used by both dev and prod. To override for prod only, add an `image:` in `docker-compose.prod.yaml`.
- Local control: create a `.env` with:
  ```env
  IMAGE_NAME=vijesh93/qgis-automation
  IMAGE_TAG=2026-02-10-dev
  ```

**Running Tests / Scripts**
- Run a quick Python import test for QGIS inside the container:
  ```powershell
  docker-compose exec qgis-app python3 -c "from qgis.core import QgsApplication; print('QGIS OK')"
  ```
- Run your test script:
  ```powershell
  docker-compose exec qgis-app python3 test/test_db_connection.py
  ```

**Common Troubleshooting**
- DNS / BuildKit token errors: if you see `failed to fetch oauth token: dial tcp: lookup auth.docker.io: no such host` during build, try disabling BuildKit temporarily:
  ```powershell
  $env:DOCKER_BUILDKIT='0'
  docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d --build
  Remove-Item Env:\DOCKER_BUILDKIT
  ```
- Container exits immediately in prod but runs in dev: dev override uses `command: tail -f /dev/null` and `tty: true` to keep the container alive for debugging; prod runs the real `CMD` from the Dockerfile which will exit on runtime errors. Inspect logs:
  ```powershell
  docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml logs --tail=200 qgis-app
  ```
- PEP 668 / pip install errors in build: we install your Python dependencies into a venv in the image to avoid `externally-managed-environment` errors. If you still see Python import errors (e.g. `ModuleNotFoundError: No module named 'PyQt5'`), verify the base image contains system PyQt5 or install `python3-pyqt5` in the Dockerfile.

**Proxy / Corporate Networks**
- Do not hardcode proxy secrets in the `Dockerfile`. Use build `ARG`s and pass them at build time or use a local `.env` (gitignored) or CI secrets. Example in `docker-compose.yaml` uses env interpolation for `HTTP_PROXY` and `HTTPS_PROXY`.

**Debugging Tips**
- View merged compose config to see the final service definition:
  ```powershell
  docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml config
  ```
- Start an interactive shell in the built prod image for debugging:
  ```powershell
  docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml run --rm qgis-app bash
  ```
- Check local images and tags:
  ```powershell
  docker images | Select-String 'qgis-automation' -SimpleMatch
  ```

**CI / Pushing Images**
- In CI, set `IMAGE_NAME` and `IMAGE_TAG` from secrets and use unique tags (commit SHA or release version). Use `docker push` or `docker/build-push-action` to push artifacts.

If you want, I can add:
- a `make` target to build and tag prod images, or
- a small `scripts/build.ps1` helper to set env variables and run compose on Windows.

---

Project files of interest:
- `Dockerfile` — image build recipe
- `docker-compose.yaml` — base service definition
- `docker-compose.dev.yaml` — development overrides (mounts, debug command)
- `docker-compose.prod.yaml` — production overrides
- `.env.example` — example environment variables

License: (none specified)

**Makefile targets**
- `make dev` — start dev compose (with source mounted).
- `make dev_build` — remove existing dev container (if any) and start a fresh dev container with build.
- `make build-dev` — build dev image only.
- `make build-prod` — build prod image only.
- `make prod` — start prod compose (build if needed).
- `make prod_push` — build and push prod image (requires `docker login`).
- `make clean` — remove compose-managed containers, local images and volumes where possible.

**scripts/build.ps1**
Use `scripts/build.ps1` as a convenient PowerShell helper that:
- loads a local `.env` (if present),
- accepts overrides for `IMAGE_NAME` and `IMAGE_TAG`,
- selects `dev` or `prod` profile, and
- runs `docker-compose build` (optionally `push` and `up`).

Examples (PowerShell):
```powershell
# Build dev using .env values
.\scripts\build.ps1 -Profile dev -Up

# Build prod, override tag and push
.\scripts\build.ps1 -Profile prod -ImageTag "2026-02-10-prod" -Push
```
