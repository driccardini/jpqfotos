from bs4 import BeautifulSoup

def parse_drive_folders(html):
    """
    Extrae una lista de dicts con 'id', 'title', 'is_folder' y 'link' de la estructura HTML de Google Drive (flip-entry).
    """
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    for entry_div in soup.find_all('div', class_='flip-entry'):
        entry_id = entry_div.get('id', '').replace('entry-', '')
        title_div = entry_div.find('div', class_='flip-entry-title')
        a_tag = entry_div.find('a', href=True)
        is_folder = False
        link = ''
        if a_tag:
            href = a_tag['href']
            link = href
            if '/drive/folders/' in href:
                is_folder = True
        if entry_id and title_div:
            title = title_div.get_text(strip=True)
            entries.append({'id': entry_id, 'title': title, 'is_folder': is_folder, 'link': link})
    return entries
