from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import divulgacao_agend, cursos
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
        rede_social = request.POST.get('rede_social')
        tipo_post = request.POST.get('tipo')
        legenda = request.POST.get('legenda')
        hora = request.POST.get('hora_pub')
        midia_original = request.FILES.get('midia')
        
        midia_final = midia_original
        
        if midia_original:
            ext = os.path.splitext(midia_original.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png']:
                try:
                    img = Image.open(midia_original)
                    img = img.convert('RGB')
                    
                    # --- CONFIGURAÇÃO DE COR ESTÁTICA (#050D35) ---
                    # Convertido de Hex para RGB: (5, 13, 53)
                    cor_fundo_estatica = (16, 26, 75)
                    
                    tipo_check = str(tipo_post).strip().capitalize()
                    
                    if tipo_check == 'Story':
                        largura_f, altura_f = 1080, 1920
                        # Aumentado para 1050 (deixa apenas uma margem mínima de 15px lateral)
                        tamanho_max_foto = 1335
                    else:
                        largura_f, altura_f = 1080, 1080
                        # No Feed, 1080 ocupa a largura total (sem bordas laterais)
                        tamanho_max_foto = 1080 

                    # Redimensionar sem distorcer
                    img.thumbnail((tamanho_max_foto, tamanho_max_foto), Image.Resampling.LANCZOS)
                    
                    # Criar fundo com a cor azul Marinho Estática
                    novo_fundo = Image.new("RGB", (largura_f, altura_f), cor_fundo_estatica)
                    
                    # Centralizar a foto no fundo
                    pos_x = (largura_f - img.size[0]) // 2
                    pos_y = (altura_f - img.size[1]) // 2
                    novo_fundo.paste(img, (pos_x, pos_y))
                    
                    # Salvar com alta fidelidade
                    buffer = io.BytesIO()
                    novo_fundo.save(buffer, format='JPEG', quality=98) 
                    midia_final = ContentFile(buffer.getvalue(), name=midia_original.name)
                    
                except Exception as e:
                    print(f"Erro ao processar imagem: {e}")

        # --- DADOS PARA O BANCO ---
        dados_comuns = {
            'rede_social': rede_social,
            'tipo_post': tipo_post,
            'legenda': legenda,
            'hora': hora,
            'midia': midia_final,
            'ultima_publicacao': None
        }

        data_principal = request.POST.get('data_pub')
        data_repeticao = request.POST.get('data_rep')

        if not data_principal:
            data_principal = timezone.now().date()

        # Criação dos registros
        divulgacao_agend.objects.create(data=data_principal, **dados_comuns)

        if data_repeticao:
            divulgacao_agend.objects.create(data=data_repeticao, **dados_comuns)

        return redirect('agenda')
    
    return render(request, 'form-agd.html', {'redes': rede, 'tipos': tipo})


def listar_cursos(request):
    # Busca todos os cursos no banco
    todos_cursos = cursos.objects.all().order_by('data_inicio')
    return render(request, 'painel.html', {'cursos': todos_cursos})

def cadastrar_curso(request):
    if request.method == 'POST':
        # Captura os dados do formulário
        cursos.objects.create(
            curso=request.POST.get('curso'),
            turno=request.POST.get('turno'),
            vagas=request.POST.get('vagas') or 0,
            inscritos=request.POST.get('inscritos') or 0,
            data_inicio=request.POST.get('data_inicio')
        )
        return redirect('painel_cursos')
    
    return render(request, 'form_curso.html')