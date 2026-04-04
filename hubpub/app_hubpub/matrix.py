import os
import MySQLdb
import MySQLdb.cursors
import requests
import pytz
import time
from datetime import datetime
import sys
from PIL import Image, ImageStat # ImageStat ajuda a calcular a cor média

# --- 1. CONFIGURAÇÕES ---
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

fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)
dia_atual = agora.strftime("%Y-%m-%d")
hora_atual = agora.strftime("%H:%M")

session = requests.Session()

# --- 3. FUNÇÃO DE TRATAMENTO DE IMAGEM COM COR DINÂMICA ---

def obter_cor_predominante(img):
    """Calcula a cor média da imagem para usar no fundo."""
    # Reduz a imagem para 1x1 pixel para pegar a cor média dominante
    img_temp = img.copy().resize((1, 1), resample=Image.Resampling.BOX)
    return img_temp.getpixel((0, 0))

def ajustar_imagem_meta(caminho_imagem, tipo_post='Feed'):
    try:
        if not os.path.exists(caminho_imagem):
            return False

        # Normaliza o tipo de post (evita erros de maiúscula/minúscula)
        tipo_ajustado = str(tipo_post).strip().capitalize()

        with Image.open(caminho_imagem) as img:
            img = img.convert('RGB')
            
            # 1. Obtém a cor predominante da imagem original
            cor_fundo = obter_cor_predominante(img)
            
            # 2. Define dimensões do fundo
            if tipo_ajustado == 'Story':
                largura_fundo, altura_fundo = 1080, 1920
                tamanho_max_foto = 850 # Tamanho da miniatura central
            else:
                largura_fundo, altura_fundo = 1080, 1080
                tamanho_max_foto = 1080

            # 3. Redimensiona a foto principal sem distorcer
            img.thumbnail((tamanho_max_foto, tamanho_max_foto), Image.Resampling.LANCZOS)
            
            # 4. Cria o fundo com a cor extraída
            novo_fundo = Image.new("RGB", (largura_fundo, altura_fundo), cor_fundo)
            
            # 5. Centraliza a foto no fundo
            pos_x = (largura_fundo - img.size[0]) // 2
            pos_y = (altura_fundo - img.size[1]) // 2
            
            novo_fundo.paste(img, (pos_x, pos_y))
            
            # 6. Salva o resultado
            novo_fundo.save(caminho_imagem, "JPEG", quality=95)
            print(f"🎨 Imagem {os.path.basename(caminho_imagem)} ajustada com cor de fundo {cor_fundo}")
            return True
    except Exception as e:
        print(f"⚠️ Erro no processamento de imagem: {e}")
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
    
    tipo_ajustado = str(tipo).strip().capitalize()
    if tipo_ajustado == 'Story':
        payload['media_type'] = 'STORIES'
    else:
        payload['caption'] = texto

    try:
        res_c = session.post(url_c, data=payload).json()
        if 'id' in res_c:
            creation_id = res_c['id']
            time.sleep(20) # Aguarda processamento da Meta
            res_p = session.post(f"https://graph.facebook.com/{API_VERSION}/{INSTA_BUSINESS_ID}/media_publish",
                                 data={'creation_id': creation_id, 'access_token': PAGE_ACCESS_TOKEN})
            return res_p.status_code == 200
        else:
            print(f"Erro Container IG: {res_c}")
    except Exception as e:
        print(f"Erro IG: {e}")
    return False

# --- 5. EXECUÇÃO ---

try:
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    query = """
        SELECT * FROM app_hubpub_divulgacao_agend
        WHERE data = %s AND hora <= %s AND ultima_publicacao IS NULL
        ORDER BY hora ASC
    """
    cursor.execute(query, (dia_atual, hora_atual))
    rows = cursor.fetchall()

    if not rows:
        print("☕ Nada agendado para agora.")
        sys.exit()

    for row in rows:
        path_local = os.path.join(CAMINHO_MEDIA_LOCAL, row['midia'])
        url_img = BASE_URL_PUBLICA + row['midia']
        
        # 1. Processa a imagem com a nova lógica de cor de fundo
        ajustar_imagem_meta(path_local, row['tipo_post'])

        # 2. Postagem
        sucesso = False
        if row['rede_social'] == 'Facebook':
            sucesso = postar_facebook(path_local, row['legenda'])
        elif row['rede_social'] == 'Instagram':
            sucesso = postar_instagram(url_img, row['legenda'], row['tipo_post'])

        if sucesso:
            cursor.execute("UPDATE app_hubpub_divulgacao_agend SET ultima_publicacao = %s WHERE id = %s", 
                           (dia_atual, row['id']))
            conn.commit()
            print(f"✅ ID {row['id']} publicado com sucesso!")
            time.sleep(5)
        else:
            print(f"❌ Falha no ID {row['id']}.")

except Exception as e:
    print(f"🚨 Erro Geral: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()