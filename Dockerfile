FROM python:3.14-slim

# Evita arquivos .pyc e deixa o log sair na hora.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# As dependencias sao copiadas antes do resto do codigo para
# aproveitar o cache do Docker entre builds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
