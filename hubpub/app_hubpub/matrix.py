import os
import sqlite3
import requests
import pytz
import time
from datetime import datetime
import sys

# --- 1. CONFIGURAÇÕES DE CAMINHO (CORREÇÃO CHAVE) ---
# Pega a pasta onde o matrix.py está (app_hubpub)
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
# SOBE UM NÍVEL para a raiz do projeto onde o db.sqlite3 realmente mora
BASE_DIR = os.path.dirname(PASTA_ATUAL)

CAMINHO_DB = os.path.join(BASE_DIR, 'db.sqlite3')
CAMINHO_MEDIA_LOCAL = os.path.join(BASE_DIR, 'media') 
BASE_URL_PUBLICA = "https://infinitycursos.site/media/"

# --- 2. CREDENCIAIS DIRETAS (HARDCODED) ---
PAGE_ACCESS_TOKEN = 'EAAUB01Agx2YBQza2bbgTBeFh7WlDy93fs6UabSLr5Kp9uwyyqfHpAXnNpOEmZADshM1tweiZCPoSkJ1PnKdDhYnvu3pJfFmQHwAlg6Wr8Pz5EecUIfJghYAXQvermuRDiITE0YeBarWiCngZBPyY7zCvLSPJcZBVklnRWJII3p5Ab4GaIORYy550SxsSYNvCKRuM6Ds5'
FACEBOOK_PAGE_ID = '1044548165403490'
INSTA_BUSINESS_ID = '17841467620559548'
API_VERSION = 'v22.0'

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje = datetime.now(fuso_br)
dia_atual = hoje.strftime("%Y-%m-%d")
hora_atual = hoje.strftime("%H:%M")

session = None
def get_session():
    global session
    if session is None: session = requests.Session()
    return session

# --- 3. FUNÇÕES DE POSTAGEM ---
def postar_facebook(caminho, texto):
    try:
        if not os.path.exists(caminho):
            print(f"❌ Arquivo local não encontrado: {caminho}")
            return False
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
    
    try:
        res_c = get_session().post(url_c, data=payload).json()
        if 'id' in res_c:
            time.sleep(10) # Tempo para processamento da Meta
            res_p = get_session().post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish", data={'creation_id': res_c['id'], 'access_token': PAGE_ACCESS_TOKEN})
            return res_p.status_code == 200
    except: return False
    return False

# --- 4. EXECUÇÃO ---

print(f"🔍 Conectando no banco em: {CAMINHO_DB}")

try:
    conn = sqlite3.connect(CAMINHO_DB)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    # Busca agendamentos atrasados ou na hora
    cursor.execute("""
        SELECT * FROM app_hubpub_divulgacao_agend 
        WHERE hora <= ? 
        AND (ultima_publicacao IS NULL OR ultima_publicacao != ?)
        ORDER BY hora ASC
    """, (hora_atual, dia_atual))

    rows = cursor.fetchall()

    if not rows:
        print(f"☕ [{hora_atual}] Nada pendente agora.")
        conn.close()
        sys.exit()

    print(f"🚀 Encontrados {len(rows)} posts.")

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
            print(f"✅ Post {row['id']} ({row['rede_social']}) OK.")
            time.sleep(5) 
        else:
            print(f"❌ Falha no post {row['id']}.")

except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    if 'conn' in locals(): conn.close()