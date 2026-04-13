from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .models import divulgacao_agend, cursos, aluno, presenca
from django.utils import timezone
from datetime import date
import json
import io
import os
import re
import uuid
from PIL import Image
from django.core.files.base import ContentFile
from functools import wraps

# --- DECORADOR DE SEGURANÇA ---
def professor_do_curso_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        curso_id = kwargs.get('curso_id')
        curso = get_object_or_404(cursos, id=curso_id)

        # Se não for o professor do curso E não for superusuário, volta pro login
        if curso.professor != request.user and not request.user.is_superuser:
            return redirect('login') 
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- VIEWS PÚBLICAS (IMPORTANTE PARA O SEU ERRO) ---

def home(request):
    return render(request, 'home.html')

# --- VIEWS EXCLUSIVAS DO ADMINISTRADOR (REDIRECIONAM O PROFESSOR) ---

@login_required
def staff(request):
    if not request.user.is_superuser:
        # Tenta mandar o prof pro curso dele em vez de dar erro
        curso_dele = cursos.objects.filter(professor=request.user).first()
        if curso_dele:
            return redirect('gestao_alunos', curso_id=curso_dele.id)
        return redirect('login')
    return render(request, 'staff.html')

@login_required
def agenda(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    agendamentos = divulgacao_agend.objects.all()
    dados_dict = {}
    for item in agendamentos:
        if item.data:
            data_str = item.data.strftime('%Y-%m-%d')
            if data_str not in dados_dict:
                dados_dict[data_str] = []
            texto = f"{item.hora} - {item.rede_social} - {item.tipo_post} - {item.curso}"
            dados_dict[data_str].append(texto)

    db_demandas_json = json.dumps(dados_dict)
    return render(request, 'agenda.html', {'db_demandas_json': db_demandas_json})

@login_required
def forms_agenda(request):
    if request.method == 'POST':
        # 1. Coleta os dados do formulário
        curso_nome = request.POST.get('curs')
        rede_social = request.POST.get('rede_social')
        tipo_post = request.POST.get('tipo')
        legenda = request.POST.get('legenda')
        midia = request.POST.get('midia')
        data_escolhida = request.POST.get('data_pub')
        hora_escolhida = request.POST.get('hora_pub')

        tipo_post = tipo_post.lower()
        nome_arquivo = re.search(r'[^/]+$', midia).group()

        midia_final = f'divulgacao/{tipo_post}/{nome_arquivo}'


        # 2. Salva no banco
        nova_divulgacao = divulgacao_agend(
            curso=curso_nome,
            rede_social=rede_social,
            tipo_post=tipo_post,
            legenda=legenda,
            midia=midia_final,
            data=data_escolhida,
            hora=hora_escolhida
        )

        nova_divulgacao.save()
        
        return redirect('agenda')

    # --- Lógica do GET (Executada apenas se não for POST) ---
    todos_cursos = cursos.objects.all()
    
    context = {
        'todos_cursos': todos_cursos,
        'redes': ['Instagram', 'Facebook', 'LinkedIn', 'TikTok', 'WhatsApp'],
        'tipos': ['Feed', 'Story', 'Reels', 'Carrossel'],
    }

    # ATENÇÃO: Verifique se o nome do arquivo é form_agd.html ou form_divulgacao.html
    return render(request, 'form_agd.html', context)

@login_required
def listar_cursos(request):
    if not request.user.is_superuser:
        return redirect('login')
    todos_cursos = cursos.objects.all().order_by('data_inicio')
    return render(request, 'painel.html', {'cursos': todos_cursos})

@login_required
def cadastrar_curso(request):
    if not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        # Captura os arquivos
        midia_post = request.FILES.get('midia_post')
        midia_feed = request.FILES.get('midia_feed')

        # Se houver ao menos um arquivo, geramos O NOME ÚNICO aqui
        nome_aleatorio_base = str(uuid.uuid4())

        if midia_post:
            ext = os.path.splitext(midia_post.name)[1] # Pega .jpg, .png etc
            midia_post.name = f"{nome_aleatorio_base}{ext}"

        if midia_feed:
            ext = os.path.splitext(midia_feed.name)[1]
            midia_feed.name = f"{nome_aleatorio_base}{ext}"

        # Agora criamos o objeto normalmente
        novo_curso = cursos(
            curso=request.POST.get('curso'),
            turno=request.POST.get('turno'),
            vagas=request.POST.get('vagas'),
            inscritos=request.POST.get('inscritos'),
            data_inicio=request.POST.get('data_inicio'),
            legenda=request.POST.get('legenda'),
            midia_post=midia_post, # Já vai com o nome alterado
            midia_feed=midia_feed, # Já vai com o nome alterado
            professor_id=request.POST.get('professor') if request.POST.get('professor') else None
        )
        novo_curso.save()
        return redirect('painel_cursos')

    usuarios = User.objects.all()
    return render(request, 'form_curso.html', {'usuarios': usuarios})

@login_required
@professor_do_curso_required
def gestao_alunos(request, curso_id):
    curso_obj = get_object_or_404(cursos, id=curso_id)
    alunos_count = aluno.objects.filter(curso=curso_obj).count()
    return render(request, 'gestao_alunos.html', {
        'curso': curso_obj, 
        'alunos_count': alunos_count
    })

@login_required
@professor_do_curso_required
def detalhe_curso(request, curso_id):
    # Se o prof tentar o caminho "curto", empurramos ele de volta pra Gestão de Alunos
    if not request.user.is_superuser:
        return redirect('gestao_alunos', curso_id=curso_id)
    
    curso_selecionado = get_object_or_404(cursos, id=curso_id)
    return render(request, 'detalhe_curso.html', {'curso': curso_selecionado})

@login_required
@professor_do_curso_required
def inserir_aluno(request, curso_id):
    curso = get_object_or_404(cursos, id=curso_id)
    if request.method == 'POST':
        nome = str(request.POST.get('nome_aluno', '')).title()
        email = request.POST.get('email_aluno')
        cpf = request.POST.get('cpf')
        data_nasc = request.POST.get('data_nascimento') or timezone.now().date()
        
        aluno.objects.create(
            curso=curso, nome=nome, email=email, cpf=cpf, data_nascimento=data_nasc
        )
        curso.inscritos += 1
        curso.save()
        return redirect('inserir_aluno', curso_id=curso.id)

    alunos = aluno.objects.filter(curso=curso).order_by('-id')
    return render(request, 'inserir_aluno.html', {'curso': curso, 'alunos': alunos})

@login_required
@professor_do_curso_required
def excluir_aluno(request, curso_id, aluno_id):
    registro = get_object_or_404(aluno, id=aluno_id, curso=curso_id)
    curso_obj = get_object_or_404(cursos, id=curso_id)
    registro.delete()
    if curso_obj.inscritos > 0:
        curso_obj.inscritos -= 1
        curso_obj.save()
    return redirect('inserir_aluno', curso_id=curso_id)

@login_required
@professor_do_curso_required
def controle_presenca(request, curso_id):
    curso_obj = get_object_or_404(cursos, id=curso_id)
    lista_alunos = aluno.objects.filter(curso=curso_obj)
    hoje = date.today()

    if request.method == "POST":
        data_selecionada = request.POST.get('data_presenca', hoje)
        for a in lista_alunos:
            veio = request.POST.get(f'aluno_{a.id}') == 'on'
            presenca.objects.update_or_create(
                aluno=a, curso=curso_obj, data=data_selecionada,
                defaults={'presente': veio, 'status': 'P' if veio else 'A'}
            )
        return redirect('gestao_alunos', curso_id=curso_id)

    return render(request, 'controle_presenca.html', {
        'curso': curso_obj, 
        'alunos': lista_alunos, 
        'hoje': hoje.strftime('%Y-%m-%d')
    })

@login_required
@professor_do_curso_required
def historico_presenca(request, curso_id):
    curso_obj = get_object_or_404(cursos, id=curso_id)
    
    # Busca todas as presenças deste curso, ordenadas pela data mais recente
    # Usamos prefetch_related para otimizar a busca dos nomes dos alunos
    historico = presenca.objects.filter(curso=curso_obj).select_related('aluno').order_by('-data', 'aluno__nome')

    return render(request, 'historico_presenca.html', {
        'curso': curso_obj,
        'historico': historico
    })

# --- CLASSE DE LOGIN ---

class MeuLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        curso_vinculado = cursos.objects.filter(professor=user).first()
        
        if curso_vinculado:
            return reverse('gestao_alunos', kwargs={'curso_id': curso_vinculado.id})
        
        if user.is_staff:
            return '/staff/'
            
        return reverse('home')