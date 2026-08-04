import pandas as pd
import os
from datetime import datetime

def compiler_et_filtrer(chemin_fichier="details_vols_aircorsica.csv"):
    if not os.path.exists(chemin_fichier):
        print("❌ Fichier CSV introuvable.")
        return

    df = pd.read_csv(chemin_fichier)
    
    # Conversion des dates avec dayfirst=True pour les deux colonnes
    try:
        df['dt_capture'] = pd.to_datetime(df['Date Interrogation'], errors='coerce', dayfirst=True)
        df['dt_vol'] = pd.to_datetime(df['Date Vol'], errors='coerce', dayfirst=True)
        
        # Calcul de l'anticipation en jours
        df['Jours_Avance'] = (df['dt_vol'] - df['dt_capture']).dt.days
        
        # Filtrer uniquement les observations faites au moins 7 jours à l'avance
        df_filtre = df[df['Jours_Avance'] >= 7].copy()
    except Exception as e:
        print(f"⚠️ Erreur lors du traitement des dates, application d'un filtre souple : {e}")
        df_filtre = df.copy()

    # Extraction de la valeur numérique du prix Light TTC pour les calculs
    if 'Light (€)' in df_filtre.columns:
        prix_col = 'Light (€)'
    else:
        prix_col = [c for c in df_filtre.columns if 'Prix' in c or 'Light' in c][0]
        
    df_filtre['Prix_num'] = df_filtre[prix_col].astype(str).str.extract(r'(\d+[.,]?\d*)')[0].str.replace(',', '.').astype(float)

    print(f"\n📊 --- COMPILATION DES SÉRIES CHRONOLOGIQUES (Anticipation >= 7 jours) ---")
    print(f"Nombre total de relevés éligibles : {len(df_filtre)}\n")
    return df_filtre

if __name__ == "__main__":
    compiler_et_filtrer()
