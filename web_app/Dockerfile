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

# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Exposition du port 8002 vers l'extérieur
EXPOSE 8002

# Commande pour exécuter Gunicorn avec votre application WSGI
CMD ["gunicorn", "--bind", ":8002", "prbmg.wsgi:application"]

