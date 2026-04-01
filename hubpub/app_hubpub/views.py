from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import divulgacao_agend
from django.utils import timezone
import json

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
        # 1. Captura os dados básicos que são iguais para ambos os posts
        dados_comuns = {
            'rede_social': request.POST.get('rede_social'),
            'tipo_post': request.POST.get('tipo'), # No seu HTML o name é 'tipo'
            'legenda': request.POST.get('legenda'),
            'hora': request.POST.get('hora_pub'),
            'midia': request.FILES.get('midia'),
            'ultima_publicacao': None  # Garante que o matrix.py veja como pendente
        }

        # 2. Captura as datas do formulário
        data_principal = request.POST.get('data_pub')
        data_repeticao = request.POST.get('data_rep') # Campo novo do JS

        # Fallback de segurança para a data principal
        if not data_principal:
            data_principal = timezone.now().date()

        # 3. Cria o Primeiro Registro (Data Principal)
        divulgacao_agend.objects.create(
            data=data_principal,
            **dados_comuns
        )

        # 4. Condicional: Cria o Segundo Registro (Repetição) apenas se houver data
        if data_repeticao:
            divulgacao_agend.objects.create(
                data=data_repeticao,
                **dados_comuns
            )

        return redirect('agenda')
    
    return render(request, 'form-agd.html', {'redes': rede, 'tipos': tipo})


