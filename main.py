import json
import asyncio
from playwright.async_api import async_playwright

async def scrape_leboncoin():
    ads_data = []
    url = "https://www.leboncoin.fr/recherche?category=2&text=polo%205&u_car_brand=VOLKSWAGEN&owner_type=pro"
    
    async with async_playwright() as p:
        # Lancement du navigateur
        browser = await p.chromium.launch(headless=False)
        
        # Utilisation d'un User-Agent très récent et configuration du viewport
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # # Appliquer le mode stealth (version async)
        # await stealth_async(page)
        
        print(f"Navigation vers {url}...")
        # On utilise un timeout plus long et wait_until="load" pour être sûr
        await page.goto(url, wait_until="load", timeout=60000)
        
        # Attente humaine aléatoire
        await asyncio.sleep(5)
        
        # Gestion des cookies
        try:
            print("Tentative d'acceptation des cookies...")
            cookie_button = await page.wait_for_selector("#didomi-notice-agree-button", timeout=5000)
            if cookie_button:
                await cookie_button.click()
                print("Cookies acceptés.")
                await asyncio.sleep(2)
        except Exception:
            print("Pas de bannière de cookies détectée ou erreur lors du clic.")

        # Scroll pour simuler une activité humaine et charger le contenu
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        
        # Sélection des cartes d'annonces
        ad_cards = await page.query_selector_all('article[data-testid="adcard"]')
        
        print(f"Nombre d'annonces trouvées : {len(ad_cards)}")
        
        for card in ad_cards:
            try:
                # Extraction des données avec await car on est en async
                title_el = await card.query_selector('[data-testid="adcard-title"]')
                price_el = await card.query_selector('[data-testid="price"]')
                location_el = await card.query_selector('[data-testid="adcard-location"]')
                link_el = await card.query_selector('a')
                
                title = await title_el.inner_text() if title_el else "N/A"
                price = await price_el.inner_text() if price_el else "N/A"
                location_text = await location_el.inner_text() if location_el else "N/A"
                
                raw_href = await link_el.get_attribute("href") if link_el else None
                link = "https://www.leboncoin.fr" + raw_href if raw_href else "N/A"
                
                location_parts = location_text.split('\n')
                city_cp = location_parts[0] if len(location_parts) > 0 else "N/A"
                date_published = location_parts[1] if len(location_parts) > 1 else "N/A"
                
                ads_data.append({
                    "title": title,
                    "price": price,
                    "location": city_cp,
                    "date": date_published,
                    "url": link
                })
                
            except Exception as e:
                print(f"Erreur lors de l'extraction d'une annonce : {e}")
        
        await browser.close()
        
    # Sauvegarde dans un fichier JSON
    if ads_data:
        with open("ads.json", "w", encoding="utf-8") as f:
            json.dump(ads_data, f, ensure_ascii=False, indent=4)
        print(f"Succès : {len(ads_data)} annonces sauvegardées dans ads.json")
    else:
        print("Aucune donnée n'a pu être extraite.")

if __name__ == "__main__":
    asyncio.run(scrape_leboncoin())
