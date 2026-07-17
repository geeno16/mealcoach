FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"

WORKDIR /tmp/build

COPY backend/dependencies.txt ./dependencies.txt

RUN pip install --upgrade pip==25.0.1 \
    && pip install -r dependencies.txt

WORKDIR /workspace


FROM base AS node

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*


FROM node AS dev


FROM node AS frontend

ENV DATABASE_URL=postgresql+asyncpg://build:build@localhost:5432/build \
    SECRET_KEY=build \
    ALGORITHM=HS256 \
    ACCESS_TOKEN_EXPIRE_MINUTES=1

COPY backend /workspace/backend
COPY frontend /workspace/frontend

WORKDIR /workspace/backend

RUN python -c "import json; from src import app; open('/tmp/openapi.json', 'w').write(json.dumps(app.openapi()))"

WORKDIR /workspace/frontend

RUN npm install \
    && OPENAPI_FILE=/tmp/openapi.json npm run gen:api \
    && npm run build


FROM base AS prod

COPY backend /workspace/backend
COPY --from=frontend /workspace/frontend/dist /workspace/frontend/dist

WORKDIR /workspace/backend

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
