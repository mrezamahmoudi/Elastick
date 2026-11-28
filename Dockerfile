# --- Elastick -------------------------------------------------------------
# Syntax: docker build -t elastick .
#
# Stage 1 builds the React UI (ui/ -> ui/dist).
# Stage 2 is the Python service and serves the built UI at /ui.

FROM node:20-alpine AS ui-build
WORKDIR /ui
COPY ui/package.json ./
RUN npm install --no-audit --no-fund
COPY ui/ .
RUN npm run build

FROM python:3.13-alpine

# Do not write .pyc files; stream logs straight out (uvicorn output in `docker logs`).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached between code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the pre-built UI bundle.
COPY app ./app
COPY --from=ui-build /ui/dist ./ui/dist

# Run as an unprivileged user (the "nobody/nobody" pair ships with Alpine).
USER nobody:nobody

EXPOSE 8000

# --proxy-headers: trust X-Forwarded-* from a reverse proxy in front of us.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
