
import streamlit as st
import requests
import html
from drive_parser import parse_drive_folders
from functools import lru_cache

st.set_page_config(page_title="JPQ Fotos", layout="wide")

# --- CONFIGURACIÓN ---
ZONAS_ROOT = "12mvWd_ppV1mHr0GRoaArAqTWYXopTAWt"  # id de la subcarpeta ZONAS (actualizado)
LLAVES_ROOT = "119We02AjgqcHLpBDXRSQAXPAblTJYCvI"  # id de la subcarpeta LLAVES
ROOTS = {"ZONAS": ZONAS_ROOT, "LLAVES": LLAVES_ROOT}



@lru_cache(maxsize=32)
def get_folder_entries(folder_id, cache_version="v1"):
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    page = requests.get(url, timeout=20).text
    # Guardar el HTML crudo en un atributo de la función para depuración
    get_folder_entries._last_html = page
    get_folder_entries._last_html_folder = folder_id
    entries = []
    try:
        parsed = parse_drive_folders(page)
        for entry in parsed:
            entries.append({
                'id': entry['id'],
                'title': html.unescape(entry['title']),
                'is_folder': entry.get('is_folder', False),
                'link': entry.get('link', '')
            })
    except Exception as e:
        # Si BeautifulSoup falla, mostrar error genérico
        raise RuntimeError(f"Error al parsear la carpeta de Google Drive: {e}")
    if not entries:
        # Buscar indicios de login o error en el HTML
        if 'serviceLogin' in page or 'Sign in' in page or 'Inicia sesión' in page:
            raise RuntimeError("No se puede acceder a la carpeta de Google Drive: requiere permisos o login. Verifica que la carpeta sea pública.")
        if 'Google Drive - Error' in page or 'No se encuentra' in page or 'not found' in page:
            raise RuntimeError("No se puede acceder a la carpeta de Google Drive: carpeta no encontrada o eliminada.")
        # Si no, error genérico
        raise RuntimeError("No se encontraron entradas en la carpeta de Google Drive. Puede que la estructura haya cambiado, la carpeta esté vacía o no sea pública.")
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
    etapa = st.selectbox("Etapa (ZONAS o LLAVES)", list(ROOTS.keys()))
    try:
        # Primer nivel: RAMA (subcarpetas directas de la ETAPA seleccionada)
        rama_folders = [f for f in get_folder_entries(ROOTS[etapa]) if f['is_folder']]
        if not rama_folders:
            st.error("No se encontraron ramas para la ETAPA seleccionada.")
            return
        ramas = [f['title'] for f in rama_folders]
        rama = st.selectbox("Rama (Caballeros, Damas, etc.)", ramas)
        rama_folder = next((f for f in rama_folders if f['title'] == rama), None)
        if not rama_folder:
            st.error("No se encontró la RAMA seleccionada.")
            return
        # Segundo nivel: CATEGORÍA (subcarpetas directas de la RAMA seleccionada)
        cat_folders = [f for f in get_folder_entries(rama_folder['id']) if f['is_folder']]
        if not cat_folders:
            st.error("No se encontraron categorías para la RAMA seleccionada.")
            return
        categorias = [f['title'] for f in cat_folders]
        categoria = st.selectbox("Categoría", categorias)
        cat_folder = next((f for f in cat_folders if f['title'] == categoria), None)
        if not cat_folder:
            st.error("No se encontró la CATEGORÍA seleccionada.")
            return
        # Tercer nivel: DÍA (subcarpetas directas de la CATEGORÍA seleccionada)
        dia_folders = [f for f in get_folder_entries(cat_folder['id']) if f['is_folder']]
        if not dia_folders:
            st.error("No se encontraron días para la CATEGORÍA seleccionada.")
            return
        dias = [f['title'] for f in dia_folders]
        dia = st.selectbox("Día", dias)
        dia_folder = next((f for f in dia_folders if f['title'] == dia), None)
        if not dia_folder:
            st.error("No se encontró el DÍA seleccionado.")
            return
        # Cuarto nivel: archivos (solo archivos directos en la carpeta del DÍA seleccionado)
        files = [f for f in get_folder_entries(dia_folder['id']) if not f['is_folder']]
        st.write(f"Fotos: {len(files)}")
        render_photo_grid(files)
    except RuntimeError as e:
        st.error(str(e))

# --- Función para mostrar el HTML crudo recibido de Google Drive (debug) ---


if __name__ == "__main__":
    main()
