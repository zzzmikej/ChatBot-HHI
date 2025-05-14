import requests
import os
import re
from tqdm import tqdm

try:
    from config import settings as actual_settings
    settings = actual_settings
except ImportError:
    print("Aviso: Não foi possível importar 'config.settings'. Usando placeholders. Certifique-se que 'config.py' está acessível.")
try:
    from views.fetcher import fetch_all_pages, save_pages
    pass 
except ImportError:
    print("Aviso: Não foi possível importar de 'views.fetcher'. As funções definidas localmente serão usadas.")


email = settings.EMAIL
api_token = settings.API_TOKEN
save_folder = settings.HTML_DOCS_PATH 
base_url = settings.BASE_URL
space_keys = [
    "ags", "API", "CM", "CME", "CMSup", "CMSupE", "CRS", "CST",
    "EMS", "HE", "HEYC", "Hstays", "hpn", "MAN", "OMS", "OPA",
    "PDP", "PDOC", "PMS", "pneng", "pnsup", "POS", "WIKI", "WSS"
]
auth = (email, api_token)

os.makedirs(save_folder, exist_ok=True)

def clean_filename(name):
    name = re.sub(r'[<>:"/\\|?*\t]', '_', name)
    name = name.replace(';', '_')
    return name

def fetch_all_pages(space_key):
    start = 0
    limit = 50
    pages = []

    while True:
        url = f"{base_url}/rest/api/content?spaceKey={space_key}&limit={limit}&start={start}&expand=body.storage"
        try:
            response = requests.get(url, auth=auth, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            break

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            break
        
        current_pages = data.get('results', [])
        pages.extend(current_pages)

        if not current_pages or len(current_pages) < limit:
            break

        start += limit
    return pages

def save_pages(pages, space_key):

    space_specific_folder = os.path.join(save_folder, space_key)
    os.makedirs(space_specific_folder, exist_ok=True)
    
    saved_count = 0
    skipped_count = 0

    for page in tqdm(pages, desc=f"Salvando páginas do espaço {space_key}"):
        title = clean_filename(page['title'])
        file_path = os.path.join(space_specific_folder, f"{title}.html")

        if os.path.exists(file_path):
            skipped_count += 1
            continue
        try:
            body_html = page['body']['storage']['value']
        except (KeyError, TypeError):
            continue

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(body_html)
            saved_count += 1
        except IOError as e:
            print(f"Erro ao salvar o arquivo {file_path}: {e}")
            
def download_main():
    for space_key in space_keys:
        pages = fetch_all_pages(space_key)
        if pages:
            save_pages(pages, space_key)
    print("\nDownload de todas as páginas concluído.")