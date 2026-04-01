import os
import sqlite3
import requests
import pytz
import time
from datetime import datetime
import sys

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.join(BASE_DIR, 'db.sqlite3')
CAMINHO_MEDIA_LOCAL = os.path.join(BASE_DIR, 'media') 
BASE_URL_PUBLICA = "https://infinitycursos.site/media/"

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje = datetime.now(fuso_br)
dia_atual = hoje.strftime("%Y-%m-%d")
hora_atual = hoje.strftime("%H:%M")

PAGE_ACCESS_TOKEN = 'EAAUB01Agx2YBQza2bbgTBeFh7WlDy93fs6UabSLr5Kp9uwyyqfHpAXnNpOEmZADshM1tweiZCPoSkJ1PnKdDhYnvu3pJfFmQHwAlg6Wr8Pz5EecUIfJghYAXQvermuRDiITE0YeBarWiCngZBPyY7zCvLSPJcZBVklnRWJII3p5Ab4GaIORYy550SxsSYNvCKRuM6Ds5'
FACEBOOK_PAGE_ID = '1044548165403490'
INSTA_BUSINESS_ID = '17841467620559548'
API_VERSION = 'v22.0'

session = None
def get_session():
    global session
    if session is None: session = requests.Session()
    return session

# --- FUNÇÕES DE POSTAGEM (Resumidas para o exemplo) ---
def postar_facebook(caminho, texto):
    try:
        with open(caminho, 'rb') as foto:
            payload = {'caption': texto, 'access_token': PAGE_ACCESS_TOKEN}
            res = get_session().post(f"https://graph.facebook.com/{API_VERSION}/{FACEBOOK_PAGE_ID}/photos", data=payload, files={'source': foto})
            return res.status_code == 200
    except: return False

def postar_instagram(url, texto, tipo='Feed'):
    url_c = f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media"
    payload = {'image_url': url, 'access_token': PAGE_ACCESS_TOKEN}
    if tipo == 'Story': payload['media_type'] = 'STORIES'
    else: payload['caption'] = texto
    
    res_c = get_session().post(url_c, data=payload).json()
    if 'id' in res_c:
        time.sleep(10)
        res_p = get_session().post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish", data={'creation_id': res_c['id'], 'access_token': PAGE_ACCESS_TOKEN})
        return res_p.status_code == 200
    return False

# --- EXECUÇÃO COM LÓGICA DE RECUPERAÇÃO ---

try:
    conn = sqlite3.connect(CAMINHO_DB)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    # MUDANÇA CHAVE: Buscamos tudo que a hora seja MENOR ou IGUAL a agora
    # E que ainda não foi publicado hoje.
    cursor.execute("""
        SELECT * FROM app_hubpub_divulgacao_agend 
        WHERE hora <= ? 
        AND (ultima_publicacao IS NULL OR ultima_publicacao != ?)
        ORDER BY hora ASC
    """, (hora_atual, dia_atual))

    rows = cursor.fetchall()

    if not rows:
        print(f"☕ [{hora_atual}] Tudo em dia. Saindo...")
        conn.close()
        sys.exit()

    print(f"⚡ Encontrados {len(rows)} posts pendentes (incluindo atrasados).")

    for row in rows:
        path_local = os.path.join(CAMINHO_MEDIA_LOCAL, row['midia'])
        url_img = BASE_URL_PUBLICA + row['midia']
        sucesso = False

        if row['rede_social'] == 'Facebook':
            sucesso = postar_facebook(path_local, row['legenda'])
        elif row['rede_social'] == 'Instagram':
            sucesso = postar_instagram(url_img, row['legenda'], row['tipo_post'])

        if sucesso:
            cursor.execute("UPDATE app_hubpub_divulgacao_agend SET ultima_publicacao = ? WHERE id = ?", (dia_atual, row['id']))
            conn.commit()
            print(f"✅ Post {row['id']} realizado com sucesso.")
            time.sleep(5) 
        else:
            print(f"❌ Falha no post {row['id']}. Tentará novamente na próxima execução.")

except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    if 'conn' in locals(): conn.close()