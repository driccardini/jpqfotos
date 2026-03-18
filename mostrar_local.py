from bs4 import BeautifulSoup

with open("last_drive_html.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for entry_div in soup.find_all('div', class_='flip-entry'):
    entry_id = entry_div.get('id', '').replace('entry-', '')
    title_div = entry_div.find('div', class_='flip-entry-title')
    title = title_div.get_text(strip=True) if title_div else '(sin título)'
    print(f"ID: {entry_id} | Título: {title}")
