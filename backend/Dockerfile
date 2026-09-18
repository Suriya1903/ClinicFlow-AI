FROM python:3.11-slim

# Prevent Python from creating .pyc files
# and make application logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install PostgreSQL client libraries and build tools.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the project's dependency file.
COPY requirements.txt /app/requirements.txt

# Install Python dependencies.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application.
COPY backend /app/backend

# Copy MCP server.
COPY mcp_server /app/mcp_server

# Copy Alembic configuration.
COPY alembic.ini /app/alembic.ini

# FastAPI port.
EXPOSE 8000

# Start FastAPI.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]