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
from PIL import Image
from django.core.files.base import ContentFile
from functools import wraps

# --- DECORADOR DE SEGURANÇA ---
def professor_do_curso_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        curso_id = kwargs.get('curso_id')
        curso = get_object_or_404(cursos, id=curso_id)

        # Se não for o professor do curso E não for superusuário, mandamos para o login
        if curso.professor != request.user and not request.user.is_superuser:
            return redirect('login') 
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- VIEWS GERAIS (SÓ ADMIN ENTRA) ---

def home(request):
    return render(request, 'home.html')

@login_required
def staff(request):
    if not request.user.is_superuser:
        # Se for professor, tentamos mandar para o curso dele, senão login
        curso_dele = cursos.objects.filter(professor=request.user).first()
        if curso_dele:
            return redirect('gestao_alunos', curso_id=curso_dele.id)
        return redirect('login')
    return render(request, 'staff.html')

@login_required
def listar_cursos(request):
    if not request.user.is_superuser:
        return redirect('login')
    todos_cursos = cursos.objects.all().order_by('data_inicio')
    return render(request, 'painel.html', {'cursos': todos_cursos})

# --- VIEWS ESPECÍFICAS DE CURSO (ÁREA CONFINADA DO PROFESSOR) ---

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
    # Se for professor, ele não vê o detalhe "administrativo", volta para a gestão de alunos
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
        # Após salvar, volta para a gestão de alunos
        return redirect('gestao_alunos', curso_id=curso_id)

    return render(request, 'controle_presenca.html', {
        'curso': curso_obj, 
        'alunos': lista_alunos, 
        'hoje': hoje.strftime('%Y-%m-%d')
    })

# --- LOGIN ---

class MeuLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        curso_vinculado = cursos.objects.filter(professor=user).first()
        
        if curso_vinculado:
            # O professor vai direto para a gestão de alunos
            return reverse('gestao_alunos', kwargs={'curso_id': curso_vinculado.id})
        
        if user.is_staff:
            return '/admin/'
            
        return reverse('home')