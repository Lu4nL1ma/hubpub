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
        if item.data_criacao:
            # Transforma a data do banco em '2026-03-28' (formato que o JS espera)
            data_str = item.data_criacao.strftime('%Y-%m-%d')
            
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
        # Captura os dados do formulário (verifique se o 'name' no HTML é 'data_pub')
        data_do_form = request.POST.get('data_pub') 
        
        # Se o usuário não preencheu a data, podemos usar a de hoje como fallback
        if not data_do_form:
            data_do_form = timezone.now().date()

        divulgacao_agend.objects.create(
            rede_social=request.POST.get('rede_social'),
            tipo_post=request.POST.get('tipo'),
            legenda=request.POST.get('legenda'),
            hora=request.POST.get('hora_pub'),
            midia=request.FILES.get('midia'),
            data_criacao=data_do_form  # Enviando manualmente o valor
        )
        return redirect('agenda')
    
    return render(request, 'form-agd.html', {'redes': rede, 'tipos': tipo})


