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
    'db': 'Lu4nL1ma$hub_infinity',
    'charset': 'utf8mb4'
}

DOMINIO = 'www.infinitycursos.site'
CAMINHO_MEDIA_LOCAL = os.path.join(BASE_DIR, 'media')
BASE_URL_PUBLICA = f"https://{DOMINIO}/media/"

# --- 2. CREDENCIAIS META ---
PAGE_ACCESS_TOKEN = 'EAAUqonUxIygBRMx1kIBLXql87o6U8r9ztfwbgTSyMACOWdEdxWkVx0FaqCLCykqszj6uICD46B8OZCJnlcCFvMEU1xlBhd4ZC7amFT7rsrzh3dPRGlZAI8ZBcwk4lMlhLCwZCGPZBojrChgM4cRT83bWP6nD2ofyrMD7fjymYlDkSYGPqIKlzBfZCDXvykslDKi'
FACEBOOK_PAGE_ID = '1017372608132992' #infinity #'1044548165403490' #pyforfin 
INSTA_BUSINESS_ID = '17841475046422565' #infinity #'17841467620559548' #pyforfin 
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
            res = session.post(f"https://graph.facebook.com/{API_VERSION}/{FACEBOOK_PAGE_ID}/photos", 
                               data=payload, files={'source': foto})
            return res.status_code == 200
    except Exception as e:
        print(f"Erro FB: {e}")
        return False

def postar_instagram(url, texto, tipo='Feed'):
    # Adicionamos um timestamp na URL para forçar o Instagram a ignorar o cache
    url_com_cache = f"{url}?v={int(time.time())}"
    
    url_c = f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media"
    payload = {'image_url': url_com_cache, 'access_token': PAGE_ACCESS_TOKEN}

    if str(tipo).strip().capitalize() == 'Story':
        payload['media_type'] = 'STORIES'
    else:
        payload['caption'] = texto

    try:
        res_c = session.post(url_c, data=payload).json()
        if 'id' in res_c:
            creation_id = res_c['id']
            # Aguarda o processamento da mídia pelo Instagram
            time.sleep(60)
            res_p = session.post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish",
                                 data={'creation_id': creation_id, 'access_token': PAGE_ACCESS_TOKEN})
            return res_p.status_code == 200
        else:
            print(f"Erro Container IG: {res_c}")
    except Exception as e:
        print(f"Erro IG: {e}")
    return False

# --- 4. EXECUÇÃO ---

print(f"📅 Data Hoje: {dia_atual} | ⏰ Hora Agora: {hora_atual}")

try:
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    query = """
        SELECT * FROM app_hubpub_divulgacao_agend
        WHERE data = %s
        AND hora <= %s
        AND ultima_publicacao IS NULL
        ORDER BY hora ASC
    """
    
    cursor.execute(query, (dia_atual, hora_atual))
    rows = cursor.fetchall()

    if not rows:
        print(f"☕ Nada agendado para este momento.")
        sys.exit()

    print(f"🚀 {len(rows)} post(s) encontrado(s).")

    for row in rows:
        # O 'midia' no banco já contém 'divulgacao/story/nome.jpg' ou 'divulgacao/feed/nome.jpg'
        # Portanto, o os.path.join vai montar: media/ + divulgacao/story/nome.jpg
        # Isso torna o caminho totalmente dinâmico.
        
        midia_limpa = row['midia'].strip() # Remove espaços extras por segurança
        
        # 1. Caminho Físico (Para o Facebook que lê o arquivo local)
        path_local = os.path.join(CAMINHO_MEDIA_LOCAL, midia_limpa)
        
        # 2. URL Pública (Para o Instagram que baixa a imagem via Link)
        url_img = BASE_URL_PUBLICA + midia_limpa
        
        sucesso = False

        print(f"📸 Processando ID {row['id']} | Curso: {row['curso']}")
        print(f"🔗 Caminho Detectado: {midia_limpa}")

        if row['rede_social'] == 'Facebook':
            sucesso = postar_facebook(path_local, row['legenda'])
            
        elif row['rede_social'] == 'Instagram':
            # Passamos o tipo_post para a função decidir se é Story ou Feed
            sucesso = postar_instagram(url_img, row['legenda'], row['tipo_post'])

        if sucesso:
            # Marcar como publicado para não repetir
            cursor.execute("UPDATE app_hubpub_divulgacao_agend SET ultima_publicacao = %s WHERE id = %s", 
                           (dia_atual, row['id']))
            conn.commit()
            print(f"✅ Post {row['id']} publicado com sucesso!")
            time.sleep(60) # Intervalo para evitar bloqueio das APIs
        else:
            print(f"❌ Falha ao publicar post {row['id']}. Verifique logs da API.")
            
except Exception as e:
    print(f"❌ Erro crítico: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("🔌 Conexão encerrada.")