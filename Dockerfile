FROM python:3.11
RUN apt-get update && apt-get install -y libpq-dev gcc
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "healthcare_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
