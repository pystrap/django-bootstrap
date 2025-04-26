#!/bin/bash

echo "🚀 Starting deploy..."

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Django service
systemctl restart qmodels-django

echo "✅ Deploy complete."
