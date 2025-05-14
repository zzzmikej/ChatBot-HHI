import requests
import os
import re
from tqdm import tqdm
from config import settings

def clean_filename(name):
        name = re.sub(r'[<>:"/\\|?*\t]', '_', name)
        name = name.replace(';', '_')
        return name
    
def fetch_all_pages(space_key, auth, base_url):
    start = 0
    limit = 1000
    pages = []

    while True:
        url = f"{base_url}/rest/api/content?spaceKey={space_key}&limit={limit}&start={start}&expand=body.storage"
        response = requests.get(url, auth=auth)

        if response.status_code != 200:
            print(f"Erro ao buscar páginas para o espaço {space_key}: {response.text}")
            break

        data = response.json()
        pages.extend(data['results'])

        if 'size' in data and data['size'] < limit:
            break

        start += limit

    return pages

def save_pages(pages, space_key, save_folder):
    for page in tqdm(pages, desc=f"Salvando páginas do espaço {space_key}"):
        title = clean_filename(page['title'])
        body_html = page['body']['storage']['value']

        page_folder = os.path.join(save_folder, space_key)
        os.makedirs(page_folder, exist_ok=True)

        with open(f"{page_folder}/{title}.html", "w", encoding="utf-8") as f:
            f.write(body_html)