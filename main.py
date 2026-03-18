
import streamlit as st
import requests
import re
import html
from functools import lru_cache

st.set_page_config(page_title="JPQ Fotos", layout="wide")

# --- CONFIGURACIÓN ---
ZONAS_ROOT = "12mvWd_ppV1mHr0GRoaArAqTWYXopTAWt"
LLAVES_ROOT = "1J6YKXSB9LOVHrep21_-YvSe_40qBQquJ"
ROOTS = {"ZONAS": ZONAS_ROOT, "LLAVES": LLAVES_ROOT}

ENTRY_PATTERN = re.compile(
    r'<div class="flip-entry" id="entry-(?P<id>[A-Za-z0-9_-]+)".*?'
    r'<a href="https://drive\\.google\\.com/(?P<link>(?:drive/folders|file/d)/[^\"?]+)"[^>]*>.*?'
    r'<div class="flip-entry-title">(?P<title>.*?)</div>.*?'
    r'<div class="flip-entry-last-modified"><div>(?P<last_modified>.*?)</div>',
    re.DOTALL,
)

@lru_cache(maxsize=32)
def get_folder_entries(folder_id, cache_version="v1"):
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    page = requests.get(url, timeout=20).text
    entries = []
    for m in ENTRY_PATTERN.finditer(page):
        link = m.group('link')
        is_folder = link.startswith('drive/folders/')
        entry = {
            'id': m.group('id'),
            'title': html.unescape(m.group('title')),
            'is_folder': is_folder,
            'link': link,
        }
        # Buscar thumbnail si es archivo
        if not is_folder:
            img = re.search(r'<img src="([^"]+)"', m.group(0))
            if img:
                entry['thumb'] = img.group(1)
            else:
                entry['thumb'] = ''
        entries.append(entry)
    return entries

def file_thumbnail_url(fid):
    return f"https://drive.google.com/thumbnail?id={fid}&sz=w2400"

def file_thumbnail_fallback_url(fid):
    return f"https://lh3.googleusercontent.com/d/{fid}=w2400"

@lru_cache(maxsize=128)
def get_thumbnail_bytes(url):
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.headers.get('content-type', '').startswith('image/'):
            return r.content
    except Exception:
        pass
    return None

def render_photo_grid(files):
    cols = st.columns(4)
    for idx, f in enumerate(files):
        thumb_bytes = None
        thumb_urls = [f.get('thumb',''), file_thumbnail_url(f['id']), file_thumbnail_fallback_url(f['id'])]
        for u in thumb_urls:
            if u:
                thumb_bytes = get_thumbnail_bytes(u)
                if thumb_bytes:
                    break
        with cols[idx % 4]:
            if thumb_bytes:
                st.image(thumb_bytes, use_column_width=True)
            else:
                st.write(":camera:")
            st.link_button("Abrir foto", f"https://drive.google.com/file/d/{f['id']}/view", use_container_width=True)

def main():
    st.title("JPQ Fotos")
    etapa = st.selectbox("Etapa", list(ROOTS.keys()))
    rama_folders = get_folder_entries(ROOTS[etapa])
    ramas = [f['title'] for f in rama_folders if f['is_folder']]
    rama = st.selectbox("Rama", ramas)
    rama_ids = [f['id'] for f in rama_folders if f['title'] == rama]
    if not rama_ids:
        st.error("No se encontró la rama seleccionada. Puede que la estructura de Google Drive haya cambiado o esté vacía.")
        return
    rama_id = rama_ids[0]
    cat_folders = get_folder_entries(rama_id)
    categorias = [f['title'] for f in cat_folders if f['is_folder']]
    categoria = st.selectbox("Categoria", categorias)
    cat_ids = [f['id'] for f in cat_folders if f['title'] == categoria]
    if not cat_ids:
        st.error("No se encontró la categoría seleccionada. Puede que la estructura de Google Drive haya cambiado o esté vacía.")
        return
    cat_id = cat_ids[0]
    dia_folders = get_folder_entries(cat_id)
    dias = [f['title'] for f in dia_folders if f['is_folder']]
    dia = st.selectbox("Día", dias)
    dia_ids = [f['id'] for f in dia_folders if f['title'] == dia]
    if not dia_ids:
        st.error("No se encontró el día seleccionado. Puede que la estructura de Google Drive haya cambiado o esté vacía.")
        return
    dia_id = dia_ids[0]
    files = [f for f in get_folder_entries(dia_id) if not f['is_folder']]
    st.write(f"Fotos: {len(files)}")
    render_photo_grid(files)

if __name__ == "__main__":
    main()
