FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip \
    && pip install .

COPY templates ./templates
COPY static ./static
COPY data ./data
COPY i18n ./i18n
COPY storage ./storage

ENV FLASK_APP=vehiclecodescan.app
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
