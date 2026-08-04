#!/bin/bash
set -e

echo "🚀 Lancement du pipeline..."

# 1. Scraping avec le script d'origine
python3 scraperapi.py

# 2. Nettoyage du CSV (sans la colonne TIME)
python3 clean_csv.py

# 3. Génération du dashboard
python3 generate_dashboard.py

echo "✨ Pipeline exécuté avec succès !"