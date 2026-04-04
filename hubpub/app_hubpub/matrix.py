import os
import MySQLdb
import MySQLdb.cursors
import requests
import pytz
import time
from datetime import datetime
import sys
from PIL import Image  # Certifique-se de ter instalado: pip install Pillow

# --- 1. CONFIGURAÇÕES DE CAMINHO E BANCO ---
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PASTA_ATUAL)

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

# Configuração de Tempo (Brasil)
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)
dia_atual = agora.strftime("%Y-%m-%d")
hora_atual = agora.strftime("%H:%M")

session = requests.Session()

# --- 3. FUNÇÃO DE TRATAMENTO DE IMAGEM (PILLOW) ---

def ajustar_imagem_meta(caminho_imagem, tipo_post='Feed'):
    """
    Redimensiona a imagem para os padrões da Meta:
    - Feed: Quadrado 1080x1080.
    - Story: Vertical 1080x1920 com a imagem centralizada como miniatura.
    """
    try:
        if not os.path.exists(caminho_imagem):
            return False

        with Image.open(caminho_imagem) as img:
            img = img.convert('RGB')
            
            # Configura as dimensões da 'tela' de fundo
            if tipo_post == 'Story':
                largura_fundo, altura_fundo = 1080, 1920
                tamanho_max_foto = 200  # Tamanho da miniatura no centro
            else:
                largura_fundo, altura_fundo = 1080, 1080
                tamanho_max_foto = 1080 # Ocupa o quadrado todo

            # Redimensiona a foto mantendo proporção original
            img.thumbnail((tamanho_max_foto, tamanho_max_foto), Image.Resampling.LANCZOS)
            
            # Cria o fundo branco (255, 255, 255)
            # DICA: Mude para (0, 0, 0) se preferir fundo preto para os Stories
            novo_fundo = Image.new("RGB", (largura_fundo, altura_fundo), (255, 255, 255))
            
            # Calcula posição central para colar a foto
            pos_x = (largura_fundo - img.size[0]) // 2
            pos_y = (altura_fundo - img.size[1]) // 2
            
            novo_fundo.paste(img, (pos_x, pos_y))
            
            # Sobrescreve o arquivo original
            novo_fundo.save(caminho_imagem, "JPEG", quality=95)
            print(f"✨ Imagem ajustada para {tipo_post}: {os.path.basename(caminho_imagem)}")
            return True
    except Exception as e:
        print(f"⚠️ Erro no Pillow ({tipo_post}): {e}")
        return False

# --- 4. FUNÇÕES DE POSTAGEM ---

def postar_facebook(caminho, texto):
    try:
        with open(caminho, 'rb') as foto:
            payload = {'caption': texto, 'access_token': PAGE_ACCESS_TOKEN}
            res = session.post(f"https://graph.facebook.com/{API_VERSION}/{FACEBOOK_PAGE_ID}/photos", 
                               data=payload, files={'source': foto})
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
            # Tempo para o Instagram processar a miniatura
            time.sleep(20) 
            res_p = session.post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish",
                                 data={'creation_id': creation_id, 'access_token': PAGE_ACCESS_TOKEN})
            return res_p.status_code == 200
    except Exception as e:
        print(f"Erro IG: {e}")
        return False
    return False

# --- 5. EXECUÇÃO DO FLUXO ---

print(f"📅 Data: {dia_atual} | ⏰ Hora: {hora_atual}")

try:
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Busca agendamentos pendentes
    query = """
        SELECT * FROM app_hubpub_divulgacao_agend
        WHERE data = %s AND hora <= %s AND ultima_publicacao IS NULL
        ORDER BY hora ASC
    """
    cursor.execute(query, (dia_atual, hora_atual))
    rows = cursor.fetchall()

    if not rows:
        print("☕ Nada para postar agora.")
        sys.exit()

    for row in rows:
        path_local = os.path.join(CAMINHO_MEDIA_LOCAL, row['midia'])
        url_img = BASE_URL_PUBLICA + row['midia']
        sucesso = False

        # 1. Ajusta a imagem localmente antes de qualquer coisa
        ajustar_imagem_meta(path_local, row['tipo_post'])

        # 2. Executa a postagem conforme a rede
        if row['rede_social'] == 'Facebook':
            sucesso = postar_facebook(path_local, row['legenda'])
        elif row['rede_social'] == 'Instagram':
            sucesso = postar_instagram(url_img, row['legenda'], row['tipo_post'])

        # 3. Finaliza no Banco de Dados
        if sucesso:
            cursor.execute("UPDATE app_hubpub_divulgacao_agend SET ultima_publicacao = %s WHERE id = %s", 
                           (dia_atual, row['id']))
            conn.commit()
            print(f"✅ Sucesso: ID {row['id']} postado no {row['rede_social']}")
            time.sleep(5) 
        else:
            print(f"❌ Falha: ID {row['id']} não publicado.")

except Exception as e:
    print(f"❌ Erro Crítico: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("🔌 Conexão encerrada.")