import pandas as pd

# 1. Charger les fichiers source
df_hist = pd.read_csv('historique_global.csv')
df_series = pd.read_csv('series_vols_aircorsica.csv')

# 2. Convertir l'ancien format pour qu'il corresponde au nouveau
df_series['date'] = pd.to_datetime(df_series['Date Vol'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
df_series[['origin', 'destination']] = df_series['Liaison'].str.split('-', expand=True)
df_series['min'] = df_series['Prix Min Light (€)']
df_series['max'] = df_series['Prix Max Light (€)']
df_series['avg'] = df_series['Moyenne Light (€)']
df_series['count'] = 1

# Sélectionner uniquement les colonnes utiles
df_converted = df_series[['origin', 'destination', 'date', 'min', 'max', 'avg', 'count']]

# 3. Fusionner et dédupliquer
df_full = pd.concat([df_hist, df_converted], ignore_index=True)
df_full = df_full.drop_duplicates(subset=['origin', 'destination', 'date'])
df_full = df_full.sort_values(by=['date', 'origin', 'destination']).reset_index(drop=True)

# 4. Sauvegarder le résultat final
df_full.to_csv('historique_global.csv', index=False)
print("Fusion réussie ! Fichier historique_global.csv mis à jour.")