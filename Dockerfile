FROM python:3.11-slim

# ---------------------------------------------------------
# 1. Set working directory
# ---------------------------------------------------------

WORKDIR /app


# ---------------------------------------------------------
# 2. Prevent Python from creating .pyc files and
#    enable immediate log output
# ---------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# ---------------------------------------------------------
# 3. Install Python dependencies
# ---------------------------------------------------------

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ---------------------------------------------------------
# 4. Copy application source
# ---------------------------------------------------------

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY scripts ./scripts
COPY data ./data


# ---------------------------------------------------------
# 5. Start FastAPI
# ---------------------------------------------------------

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"]