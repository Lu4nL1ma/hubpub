import os
import MySQLdb  # Substitui o sqlite3
import requests
import pytz
import time
from datetime import datetime
import sys

# --- 1. CONFIGURAÇÕES DE CAMINHO ---
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PASTA_ATUAL)

# Agora o caminho do banco não é mais um arquivo, mas os dados da aba Databases
DB_CONFIG = {
    'host': 'Lu4nL1ma.mysql.pythonanywhere-services.com',
    'user': 'Lu4nL1ma',
    'passwd': '123lux456',  # A mesma que você colocou no settings.py
    'db': 'Lu4nL1ma$app_hubpub',
    'charset': 'utf8mb4'
}

CAMINHO_MEDIA_LOCAL = os.path.join(BASE_DIR, 'media') 
BASE_URL_PUBLICA = "https://infinitycursos.site/media/"

# --- 2. CREDENCIAIS META ---
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
            time.sleep(10)
            res_p = get_session().post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish", data={'creation_id': res_c['id'], 'access_token': PAGE_ACCESS_TOKEN})
            return res_p.status_code == 200
    except: return False
    return False

# --- 4. EXECUÇÃO ---

print(f"🔍 Conectando ao MySQL: {DB_CONFIG['db']}")

try:
    # Conexão MySQL
    conn = MySQLdb.connect(**DB_CONFIG)
    # Cursor DictCursor faz o mesmo que o row_factory=sqlite3.Row (permite acessar por nome da coluna)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Busca agendamentos (A query é quase idêntica, mas MySQL usa %s em vez de ?)
    query = """
        SELECT * FROM app_hubpub_divulgacao_agend 
        WHERE hora <= %s 
        AND (ultima_publicacao IS NULL OR ultima_publicacao != %s)
        ORDER BY hora ASC
    """
    cursor.execute(query, (hora_atual, dia_atual))

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
            # Update usando %s para o MySQL
            cursor.execute("UPDATE app_hubpub_divulgacao_agend SET ultima_publicacao = %s WHERE id = %s", (dia_atual, row['id']))
            conn.commit()
            print(f"✅ Post {row['id']} ({row['rede_social']}) OK.")
            time.sleep(5) 
        else:
            print(f"❌ Falha no post {row['id']}.")

except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    if 'conn' in locals() and conn.open: conn.close()