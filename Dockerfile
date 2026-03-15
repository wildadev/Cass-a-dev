FROM python:3.12-slim AS backend

WORKDIR /app

COPY pyproject.toml .
COPY cass/ cass/
RUN pip install --no-cache-dir .

FROM node:22-slim AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --legacy-peer-deps
COPY frontend/ .
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

COPY --from=backend /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY cass/ cass/
COPY pyproject.toml .
COPY --from=frontend-build /frontend/dist /app/frontend/dist

RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite+aiosqlite:///./data/cass.db
ENV PORT=8000

EXPOSE 8000

CMD uvicorn cass.main:app --host 0.0.0.0 --port $PORT
