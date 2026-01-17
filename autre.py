import lbc
import json

client = lbc.Client()

result = client.search(
    text="polo 5",
    page=1,
    limit=10000,
    sort=lbc.Sort.NEWEST,
    ad_type=lbc.AdType.OFFER,
    category=lbc.Category.VEHICULES,
    owner_type=lbc.OwnerType.PRO,
)

# Sélection des champs spécifiques et conversion en liste de dictionnaires
ads_list = [{
    "first_publication_date": ad.first_publication_date,
    "expiration_date": ad.expiration_date,
    "index_date": ad.index_date,
    "status": ad.status,
    "category_id": ad.category_id,
    "category_name": ad.category_name,
    "subject": ad.subject,
    "body": ad.body,
    "brand": ad.brand,
    "ad_type": ad.ad_type,
    "url": ad.url,
    "price": ad.price
} for ad in result.ads]

# Sauvegarde dans le fichier JSON
with open("polo_pro.json", "w", encoding="utf-8") as f:
    json.dump(ads_list, f, ensure_ascii=False, indent=4)

print(f"Sauvegardé {len(ads_list)} annonces dans ads_lbc.json")