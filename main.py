import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import random

async def scrape_leboncoin():
    ads_data = []
    # Ton URL spécifique pour les Polo 5 VW (Pro)
    url = "https://www.leboncoin.fr/recherche?category=2&text=polo%205&u_car_brand=VOLKSWAGEN&owner_type=pro"
    
    stealth = Stealth()
    
    async with async_playwright() as p:
        # Lancement du navigateur
        browser = await p.chromium.launch(headless=False)
        
        # Configuration du contexte avec User-Agent et dimensions d'écran
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )
        
        page = await context.new_page()
        
        # Appliquer le mode stealth sur la page
        await stealth.apply_stealth_async(page)
        
        print(f"Navigation vers {url}...")
        await page.goto(url, wait_until="load", timeout=60000)
        
        # Pause pour simuler un humain
        await asyncio.sleep(random.randint(3, 5))
        
        # Gestion des cookies
        try:
            print("Tentative d'acceptation des cookies...")
            cookie_button = await page.wait_for_selector("#didomi-notice-agree-button", timeout=5000)
            if cookie_button:
                await cookie_button.click()
                print("Cookies acceptés.")
                await asyncio.sleep(random.randint(1, 3))
        except Exception:
            print("Pas de bannière de cookies détectée.")

        # Simulation de scroll
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        await asyncio.sleep(random.randint(1, 3))
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(random.randint(1, 3))
        
        # Extraction robuste en une seule fois dans le navigateur
        ads_data = await page.evaluate("""
            () => {
                const results = [];
                const cards = document.querySelectorAll('article[data-test-id="ad"]');
                
                cards.forEach(card => {
                    try {
                        const titleEl = card.querySelector('[data-test-id="adcard-title"]');
                        const priceEl = card.querySelector('[data-test-id="price"]');
                        const locationEl = card.querySelector('[data-test-id="ad-location-light"]');
                        const paramsEl = card.querySelector('[data-test-id="ad-params-light"]');
                        const linkEl = card.querySelector('a');
                        
                        const locationText = locationEl ? locationEl.innerText : "N/A";
                        const locationParts = locationText.split('\\n');
                        
                        results.push({
                            title: titleEl ? titleEl.innerText : "N/A",
                            price: priceEl ? priceEl.innerText : "N/A",
                            location: locationParts[0] || "N/A",
                            date: locationParts[1] || "N/A",
                            url: linkEl ? "https://www.leboncoin.fr" + linkEl.getAttribute('href') : "N/A",
                            params: paramsEl ? paramsEl.innerText : "N/A"
                        });
                    } catch (e) {}
                });
                return results;
            }
        """)
        
        print(f"Nombre d'annonces extraites : {len(ads_data)}")
        
        await browser.close()
        
    if ads_data:
        with open("ads2.json", "w", encoding="utf-8") as f:
            json.dump(ads_data, f, ensure_ascii=False, indent=4)
        print(f"Succès : {len(ads_data)} annonces sauvegardées dans ads.json")
    else:
        print("Aucune donnée extraite.")

if __name__ == "__main__":
    asyncio.run(scrape_leboncoin())
