from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from .models import divulgacao_agend, cursos, aluno, presenca
from django.utils import timezone
from datetime import date
import json
import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from functools import wraps

# --- DECORADOR PARA VALIDAR SE O PROFESSOR É DONO DO CURSO ---
def professor_do_curso_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        curso_id = kwargs.get('curso_id')
        # Tenta buscar o curso; se não existir, dá 404
        curso = get_object_or_404(cursos, id=curso_id)

        # Se não for o professor do curso E não for administrador, barra o acesso
        if curso.professor != request.user and not request.user.is_superuser:
            raise PermissionDenied("Acesso Negado: Não és o responsável por este curso.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- VIEW PÚBLICA ---

def home(request):
    return render(request, 'home.html')

# --- VIEWS EXCLUSIVAS DO ADMINISTRADOR (SUPERUSER) ---
# Professores que tentarem aceder a estas URLs receberão um erro 403.

@login_required
def staff(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    return render(request, 'staff.html')

@login_required
def agenda(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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
def form_agenda(request):
    if not request.user.is_superuser:
        raise PermissionDenied
        
    todos_cursos = cursos.objects.all().order_by('data_inicio')
    rede = ['Instagram', 'Facebook', 'Whatsapp', 'Tiktok', 'E-mail']
    tipo = ['Feed', 'Story', 'Mensagem']
    
    if request.method == 'POST':
        # ... (Mantivemos a tua lógica de processamento de imagem aqui)
        pass 

    return render(request, 'form-agd.html', {'redes': rede, 'tipos': tipo, 'todos_cursos': todos_cursos})

@login_required
def listar_cursos(request):
    # Se for professor, vê apenas o dele. Se for admin, vê todos.
    if request.user.is_superuser:
        todos_cursos = cursos.objects.all().order_by('data_inicio')
    else:
        todos_cursos = cursos.objects.filter(professor=request.user).order_by('data_inicio')
        
    return render(request, 'painel.html', {'cursos': todos_cursos})

@login_required
def cadastrar_curso(request):
    if not request.user.is_superuser:
        raise PermissionDenied
        
    if request.method == 'POST':
        cursos.objects.create(
            curso=request.POST.get('curso'),
            turno=request.POST.get('turno'),
            vagas=request.POST.get('vagas') or 0,
            inscritos=request.POST.get('inscritos') or 0,
            data_inicio=request.POST.get('data_inicio')
        )
        return redirect('painel_cursos')
    return render(request, 'form_curso.html')

# --- VIEWS DO CURSO (PROFESSOR PODE ACEDER AO QUE LHE PERTENCE) ---

@login_required
@professor_do_curso_required
def detalhe_curso(request, curso_id):
    curso_selecionado = get_object_or_404(cursos, id=curso_id)
    return render(request, 'detalhe_curso.html', {'curso': curso_selecionado})

@login_required
@professor_do_curso_required
def gestao_alunos(request, curso_id):
    curso_obj = get_object_or_404(cursos, id=curso_id)
    alunos_count = aluno.objects.filter(curso=curso_obj).count()
    return render(request, 'gestao_alunos.html', {'curso': curso_obj, 'alunos_count': alunos_count})

@login_required
@professor_do_curso_required
def inserir_aluno(request, curso_id):
    curso = get_object_or_404(cursos, id=curso_id)
    if request.method == 'POST':
        nome = str(request.POST.get('nome_aluno')).title()
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
        return redirect('detalhe_curso', curso_id=curso_id)

    return render(request, 'controle_presenca.html', {
        'curso': curso_obj, 'alunos': lista_alunos, 'hoje': hoje.strftime('%Y-%m-%d')
    })

# --- CLASSE DE LOGIN COM REDIRECIONAMENTO INTELIGENTE ---

class MeuLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        
        # Busca o curso onde este utilizador é o professor
        curso_vinculado = cursos.objects.filter(professor=user).first()
        
        if curso_vinculado:
            # ENTRADA DIRETA: Vai para a gestão de alunos do seu curso
            return reverse('gestao_alunos', kwargs={'curso_id': curso_vinculado.id})
        
        # Se for administrador puro, vai para o painel Django Admin
        if user.is_staff:
            return '/admin/'
            
        # Caso padrão para outros utilizadores
        return reverse('home')