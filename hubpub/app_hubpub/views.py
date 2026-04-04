from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import divulgacao_agend
from django.utils import timezone
import json
import io
import os
from PIL import Image
from django.core.files.base import ContentFile

def home(request):
  return render(request, 'home.html')

@login_required
def staff(request):
  return render(request, 'staff.html')
@login_required
def agenda(request):
    agendamentos = divulgacao_agend.objects.all()
    dados_dict = {}

    for item in agendamentos:
        # IMPORTANTE: Verifique se o valor não é None antes de formatar
        if item.data:
            # Transforma a data do banco em '2026-03-28' (formato que o JS espera)
            data_str = item.data.strftime('%Y-%m-%d')
            
            if data_str not in dados_dict:
                dados_dict[data_str] = []
            
            # Formata a string que aparece no card
            texto = f"{item.hora} - {item.rede_social}"
            dados_dict[data_str].append(texto)

    # Converte o dicionário Python para uma string JSON que o JS entende
    db_demandas_json = json.dumps(dados_dict)

    return render(request, 'agenda.html', {'db_demandas_json': db_demandas_json})
    
@login_required
def form_agenda(request):
    rede = ['Instagram', 'Facebook', 'Whatsapp', 'Tiktok', 'E-mail']
    tipo = ['Feed', 'Story', 'Mensagem']
    
    if request.method == 'POST':
        # 1. Captura os dados brutos
        rede_social = request.POST.get('rede_social')
        tipo_post = request.POST.get('tipo')
        legenda = request.POST.get('legenda')
        hora = request.POST.get('hora_pub')
        midia_original = request.FILES.get('midia')
        
        # 2. Processamento de Imagem (Pillow) dentro da View
        midia_final = midia_original
        
        if midia_original:
            ext = os.path.splitext(midia_original.name)[1].lower()
            # Só processamos se for imagem
            if ext in ['.jpg', '.jpeg', '.png']:
                try:
                    # Abre a imagem que está na memória
                    img = Image.open(midia_original)
                    img = img.convert('RGB')
                    
                    # A) Extrair a cor predominante (média da imagem)
                    cor_fundo = img.resize((1, 1)).getpixel((0, 0))
                    
                    # B) Definir as dimensões da "Tela"
                    tipo_check = str(tipo_post).strip().capitalize()
                    if tipo_check == 'Story':
                        largura_f, altura_f = 1080, 1920
                        tamanho_max_foto = 850 # Miniatura centralizada
                    else:
                        largura_f, altura_f = 1080, 1080
                        tamanho_max_foto = 1080 # Quadrado cheio

                    # C) Redimensionar a foto sem distorcer
                    img.thumbnail((tamanho_max_foto, tamanho_max_foto), Image.Resampling.LANCZOS)
                    
                    # D) Criar o fundo colorido e centralizar a foto
                    novo_fundo = Image.new("RGB", (largura_f, altura_f), cor_fundo)
                    pos_x = (largura_f - img.size[0]) // 2
                    pos_y = (altura_f - img.size[1]) // 2
                    novo_fundo.paste(img, (pos_x, pos_y))
                    
                    # E) Transformar o resultado de volta em um arquivo para o Django
                    buffer = io.BytesIO()
                    novo_fundo.save(buffer, format='JPEG', quality=90)
                    midia_final = ContentFile(buffer.getvalue(), name=midia_original.name)
                    
                except Exception as e:
                    print(f"Erro ao processar imagem: {e}")
                    # Caso dê erro, o midia_final continua sendo o midia_original

        # 3. Organiza os dados para criação no banco
        dados_comuns = {
            'rede_social': rede_social,
            'tipo_post': tipo_post,
            'legenda': legenda,
            'hora': hora,
            'midia': midia_final, # Salva a imagem já formatada
            'ultima_publicacao': None
        }

        data_principal = request.POST.get('data_pub')
        data_repeticao = request.POST.get('data_rep')

        if not data_principal:
            data_principal = timezone.now().date()

        # 4. Criação dos registros no Banco de Dados
        # Registro 01
        divulgacao_agend.objects.create(
            data=data_principal,
            **dados_comuns
        )

        # Registro 02 (Repetição)
        if data_repeticao:
            divulgacao_agend.objects.create(
                data=data_repeticao,
                **dados_comuns
            )

        return redirect('agenda')
    
    return render(request, 'form-agd.html', {'redes': rede, 'tipos': tipo})

