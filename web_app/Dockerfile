# Utilisation de l'image de base Python 3.10 slim
FROM python:3.10-slim

# Définition des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier requirements.txt dans le conteneur
COPY ./requirements.txt /app/requirements.txt

# Installation des dépendances
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copie de l'ensemble du projet dans le conteneur
COPY . /app

RUN apt-get update \
    && apt-get install -y \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Exposition du port 8002 vers l'extérieur
EXPOSE 8002

# Commande pour exécuter Gunicorn avec votre application WSGI
CMD ["gunicorn", "--bind", ":8002", "prbmg.wsgi:application"]

