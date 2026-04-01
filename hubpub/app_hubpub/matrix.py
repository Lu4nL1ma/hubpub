import os
import MySQLdb
import MySQLdb.cursors
import requests
import pytz
import time
from datetime import datetime
import sys

# --- 1. CONFIGURAÇÕES DE CAMINHO ---
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PASTA_ATUAL)

# Configurações do MySQL
DB_CONFIG = {
    'host': 'Lu4nL1ma.mysql.pythonanywhere-services.com',
    'user': 'Lu4nL1ma',
    'passwd': '123lux456',
    'db': 'Lu4nL1ma$app_hubpub',
    'charset': 'utf8mb4'
}

CAMINHO_MEDIA_LOCAL = os.path.join(BASE_DIR, 'media')
BASE_URL_PUBLICA = "https://lu4nl1ma.pythonanywhere.com/media/"

# --- 2. CREDENCIAIS META ---
PAGE_ACCESS_TOKEN = 'EAAUB01Agx2YBQza2bbgTBeFh7WlDy93fs6UabSLr5Kp9uwyyqfHpAXnNpOEmZADshM1tweiZCPoSkJ1PnKdDhYnvu3pJfFmQHwAlg6Wr8Pz5EecUIfJghYAXQvermuRDiITE0YeBarWiCngZBPyY7zCvLSPJcZBVklnRWJII3p5Ab4GaIORYy550SxsSYNvCKRuM6Ds5'
FACEBOOK_PAGE_ID = '1044548165403490'
INSTA_BUSINESS_ID = '17841467620559548'
API_VERSION = 'v22.0'

# Ajuste de Fuso Horário (Brasil - São Paulo)
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)
dia_atual = agora.strftime("%Y-%m-%d")
hora_atual = agora.strftime("%H:%M")

session = requests.Session()

# --- 3. FUNÇÕES DE POSTAGEM ---
def postar_facebook(caminho, texto):
    try:
        if not os.path.exists(caminho):
            print(f"❌ Arquivo local não encontrado: {caminho}")
            return False
        with open(caminho, 'rb') as foto:
            payload = {'caption': texto, 'access_token': PAGE_ACCESS_TOKEN}
            res = session.post(f"https://graph.facebook.com/{API_VERSION}/{FACEBOOK_PAGE_ID}/photos", data=payload, files={'source': foto})
            return res.status_code == 200
    except Exception as e:
        print(f"Erro FB: {e}")
        return False

def postar_instagram(url, texto, tipo='Feed'):
    url_c = f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media"
    payload = {'image_url': url, 'access_token': PAGE_ACCESS_TOKEN}

    if tipo == 'Story':
        payload['media_type'] = 'STORIES'
    else:
        payload['caption'] = texto

    try:
        res_c = session.post(url_c, data=payload).json()
        if 'id' in res_c:
            creation_id = res_c['id']
            # Aguarda o processamento da mídia pelo Instagram
            time.sleep(15)
            res_p = session.post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish",
                                 data={'creation_id': creation_id, 'access_token': PAGE_ACCESS_TOKEN})
            return res_p.status_code == 200
    except Exception as e:
        print(f"Erro IG: {e}")
        return False
    return False

# --- 4. EXECUÇÃO ---

print(f"📅 Data Hoje: {dia_atual} | ⏰ Hora Agora: {hora_atual}")
print(f"🔍 Buscando agendamentos pendentes para hoje...")

try:
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # QUERY LIMPA: Busca apenas o que é de HOJE, já passou da HORA e NUNCA foi publicado
    query = """
        SELECT * FROM app_hubpub_divulgacao_agend
        WHERE data = %s
        AND hora <= %s
        AND ultima_publicacao IS NULL
        ORDER BY hora ASC
    """
    
    # Passamos exatamente 2 argumentos para preencher os 2 '%s' da query
    cursor.execute(query, (dia_atual, hora_atual))
    rows = cursor.fetchall()

    if not rows:
        print(f"☕ Nada agendado para este exato momento.")
        sys.exit()

    print(f"🚀 {len(rows)} post(s) encontrado(s). Iniciando processamento...")

    for row in rows:
        path_local = os.path.join(CAMINHO_MEDIA_LOCAL, row['midia'])
        url_img = BASE_URL_PUBLICA + row['midia']
        sucesso = False

        print(f"📸 Processando ID {row['id']} para {row['rede_social']}...")

        if row['rede_social'] == 'Facebook':
            sucesso = postar_facebook(path_local, row['legenda'])
        elif row['rede_social'] == 'Instagram':
            sucesso = postar_instagram(url_img, row['legenda'], row['tipo_post'])

        if sucesso:
            # Marca como finalizado para não repetir nunca mais
            cursor.execute("UPDATE app_hubpub_divulgacao_agend SET ultima_publicacao = %s WHERE id = %s", (dia_atual, row['id']))
            conn.commit()
            print(f"✅ Post {row['id']} publicado com sucesso!")
            time.sleep(5) 
        else:
            print(f"❌ Falha ao publicar post {row['id']}. Ficará para a próxima tentativa.")

except Exception as e:
    print(f"❌ Erro crítico: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("🔌 Conexão com banco encerrada.")