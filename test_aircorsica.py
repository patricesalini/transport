import asyncio
import re
import os
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("🚀 Lancement du navigateur...", flush=True)
        
        user_data_dir = "./chrome_profile"
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="fr-FR",
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

        await page.goto("https://www.aircorsica.com/billet-avion/acheter-un-billet.html", wait_until="domcontentloaded")
        await page.bring_to_front()

        print("\n" + "="*60)
        print("🛑 ACTION REQUISE DANS LE NAVIGATEUR :")
        print("   1. Remplis la recherche (Ajaccio -> Paris Orly, Aller simple, date).")
        print("   2. Clique sur 'Rechercher'.")
        print("   👉 LE SCRIPT SURVEILLE L'ÉCRAN ET ATTEND TOUT SEUL LES PRIX...")
        print("="*60 + "\n", flush=True)

        print("⏳ En attente de l'affichage des résultats...", flush=True)
        
        results_found = False
        vols_data = []
        timestamp_scrap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Boucle d'attente intelligente (patiente jusqu'à 5 minutes que vous fassiez la recherche)
        for _ in range(150):
            await asyncio.sleep(2)
            
            for p_target in browser_context.pages:
                for frame in p_target.frames:
                    try:
                        txt = await frame.evaluate("document.body ? document.body.innerText : ''")
                        if not txt or len(txt.strip()) < 50:
                            continue
                        
                        # Vérifier qu'on est bien sur la page de résultats (présence d'horaires et de prix en €)
                        has_time = bool(re.search(r"\b([0-2][0-9]):([0-5][0-9])\b", txt))
                        has_euro = "€" in txt or "EUR" in txt
                        
                        if has_time and has_euro and "ACHETER UN VOL" not in txt[:150]:
                            lines = [line.strip() for line in txt.split('\n') if line.strip()]
                            
                            current_time = None
                            date_vol = "Vol direct"
                            
                            for line in lines:
                                if re.search(r"(LUN|MAR|MER|JEU|VEN|SAM|DIM|\bJAN|\bFEV|\bMAR|\bAVR|\bMAI|\bJUN|\bJUL|\bAOU|\bSEP|\bOCT|\bNOV|\bDEC)", line, re.I):
                                    if any(d in line.upper() for d in ["2026", "2027", "LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]):
                                        date_vol = line

                            temp_vols = []
                            for i, line in enumerate(lines):
                                time_match = re.search(r"\b([0-2][0-9]):([0-5][0-9])\b", line)
                                if time_match:
                                    current_time = f"{time_match.group(1)}:{time_match.group(2)}"
                                
                                if current_time:
                                    for offset in range(1, 4):
                                        if i + offset < len(lines):
                                            next_line = lines[i + offset]
                                            price_clean = next_line.replace("€", "").replace("EUR", "").strip()
                                            if re.match(r"^\d{2,4}[.,]\d{2}$", price_clean):
                                                try:
                                                    val = float(price_clean.replace(",", "."))
                                                    if 35 <= val <= 2000:
                                                        temp_vols.append({
                                                            "Date_Scraping": timestamp_scrap,
                                                            "Depart": "Ajaccio (AJA)",
                                                            "Arrivee": "Paris Orly (ORY)",
                                                            "Date_Vol": date_vol,
                                                            "Horaire": current_time,
                                                            "Prix": f"{val:.2f} €"
                                                        })
                                                except ValueError:
                                                    pass
                            if temp_vols:
                                vols_data = temp_vols
                                results_found = True
                                break
                    except Exception:
                        pass
                if results_found:
                    break
            if results_found:
                break
            print(".", end="", flush=True)

        if vols_data:
            df_new = pd.DataFrame(vols_data).drop_duplicates(subset=["Horaire", "Prix"])
            
            # Gestion du CSV : les éléments les plus récents sont positionnés tout en haut
            if os.path.exists("vols_aircorsica.csv"):
                try:
                    df_old = pd.read_csv("vols_aircorsica.csv")
                    df_final = pd.concat([df_new, df_old], ignore_index=True).drop_duplicates(subset=["Horaire", "Prix"])
                except Exception:
                    df_final = df_new
            else:
                df_final = df_new
                
            df_final.to_csv("vols_aircorsica.csv", index=False, encoding="utf-8-sig")
            print(f"\n\n✅ SUCCÈS : {len(df_new)} vol(s) extrait(s) automatiquement et enregistrés en haut du CSV !")
            print(df_new[['Horaire', 'Prix']].to_string(index=False))
        else:
            print("\n\n⚠️ Temps d'attente dépassé. Assurez-vous d'avoir bien validé la recherche dans le navigateur.")

        input("\n▶️ Appuie sur [Entrée] pour fermer le navigateur...")
        await browser_context.close()

if __name__ == "__main__":
    asyncio.run(main())