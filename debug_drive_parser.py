import requests
from drive_parser import parse_drive_folders

folder_id = "12mvWd_ppV1mHr0GRoaArAqTWYXopTAWt"
url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
page = requests.get(url, timeout=20).text

# Guardar el HTML para inspección
with open("last_drive_html.html", "w", encoding="utf-8") as f:
    f.write(page)

parsed = parse_drive_folders(page)
print(f"Entradas parseadas: {parsed}")
