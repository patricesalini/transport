import asyncio
from playwright.async_api import async_playwright

async def diagnostic():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print("Navigation vers la page de réservation...")
        await page.goto("https://www.aircorsica.com/billet-avion/acheter-un-billet.html", wait_until="domcontentloaded")
        
        input("🛑 Faites votre recherche à la main dans la fenêtre, arrivez jusqu'aux tarifs, puis appuyez sur [Entrée] ici...")
        
        for i, frame in enumerate(page.frames):
            try:
                txt = await frame.evaluate("document.body ? document.body.innerText : ''")
                print(f"--- FRAME {i} (longueur {len(txt)}) ---")
                print(txt[:1000])
            except Exception as e:
                print(f"Frame {i} erreur: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnostic())
