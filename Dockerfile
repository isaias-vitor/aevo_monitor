# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim

LABEL fly_launch_runtime="flask"

WORKDIR /code

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Define qual app Flask rodar
ENV FLASK_APP=app.py  
# 👆 troque "app.py" se o seu arquivo principal tiver outro nome

# Expõe a porta usada pelo Fly
EXPOSE 8080

# Comando para iniciar o servidor
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
