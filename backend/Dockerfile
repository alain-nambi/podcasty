FROM python:3.12-slim

# --- DÉBUT DES MODIFICATIONS POUR L'ATTENTE DB ---
# Installer bash et les utilitaires PostgreSQL (pour pg_isready)
RUN apt-get update && apt-get install -y \
    bash \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer le script d'attente pour la base de données
COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# --- FIN DES MODIFICATIONS POUR L'ATTENTE DB ---

# Le CMD est maintenant déplacé dans l'entrypoint du docker-compose.yml
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]