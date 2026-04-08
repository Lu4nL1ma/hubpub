from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import divulgacao_agend, cursos, aluno
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
            texto = f"{item.hora} - {item.rede_social} - {item.tipo_post} - {item.curso}"
            dados_dict[data_str].append(texto)

    # Converte o dicionário Python para uma string JSON que o JS entende
    db_demandas_json = json.dumps(dados_dict)

    return render(request, 'agenda.html', {'db_demandas_json': db_demandas_json})
    
@login_required
def form_agenda(request):
    todos_cursos = cursos.objects.all().order_by('data_inicio')
    rede = ['Instagram', 'Facebook', 'Whatsapp', 'Tiktok', 'E-mail']
    tipo = ['Feed', 'Story', 'Mensagem']
    
    if request.method == 'POST':
        curso = request.POST.get('curs')
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

                    # --- Trecho Corrigido dentro do seu IF ---
                    if tipo_check == 'Story':
                        largura_f, altura_f = 1080, 1920
                        limite_redimensionar = (1080, 1920) # Tupla correta
                    else:
                        largura_f, altura_f = 1080, 1080
                        limite_redimensionar = (1080, 1080) # Tupla correta

                    # Redimensionar usando a tupla definida acima
                    img.thumbnail(limite_redimensionar, Image.Resampling.LANCZOS)

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
            'curso': curso,
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
    
    return render(request, 'form-agd.html', {'redes': rede, 'tipos': tipo, 'todos_cursos': todos_cursos})


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

def detalhe_curso(request, curso_id):
    # Busca o curso pelo ID que veio da URL
    curso_selecionado = get_object_or_404(cursos, id=curso_id)
    
    # Depois incluiremos a lista de alunos e o financeiro aqui.
    context = {
        'curso': curso_selecionado,
    }
    return render(request, 'detalhe_curso.html', context)


def inserir_aluno(request, curso_id):
    # 1. Busca o curso ou retorna 404
    curso = get_object_or_404(cursos, id=curso_id)
    
    if request.method == 'POST':
        # 2. Captura os dados do formulário POST
        nome = request.POST.get('nome_aluno')
        email = request.POST.get('email_aluno')
        cpf = request.POST.get('cpf')
        data_nasc = request.POST.get('data_nascimento')

        nome = str(nome).title()

        # 3. Tratamento simples para data (evita erro se o campo vier vazio)
        if not data_nasc:
            data_nasc = timezone.now().date()

        # 4. Salva o novo aluno vinculado ao curso
        aluno.objects.create(
            curso=curso, 
            nome=nome, 
            email=email,
            cpf=cpf,
            data_nascimento=data_nasc
        )

        # 5. Atualiza o contador de inscritos do curso automaticamente
        # Isso faz a barra de progresso no painel principal subir sozinha
        curso.inscritos += 1
        curso.save()

        # 6. Redireciona para a mesma página para limpar o formulário e atualizar a lista
        return redirect('inserir_aluno', curso_id=curso.id)

    # 7. Busca todos os alunos deste curso (os mais novos primeiro)
    alunos = aluno.objects.filter(curso=curso).order_by('-id')
    
    # 8. Renderiza o template híbrido (Formulário + Tabela)
    return render(request, 'inserir_aluno.html', {
        'curso': curso,
        'alunos': alunos
    })

def excluir_aluno(request, curso_id, aluno_id):
    # O erro era o 'curso_id'. No Django, filtramos pelo nome do campo no Model.
    # Como seu campo se chama 'curso', usamos curso=curso_id
    registro = get_object_or_404(aluno, id=aluno_id, curso=curso_id)
    
    curso_obj = get_object_or_404(cursos, id=curso_id)

    # Deleta o registro do aluno
    registro.delete()

    # Atualiza o contador de inscritos do curso
    if curso_obj.inscritos > 0:
        curso_obj.inscritos -= 1
        curso_obj.save()
        
    return redirect('inserir_aluno', curso_id=curso_id)

def controle_presenca(request, curso_id):
    curso_obj = get_object_or_404(cursos, id=curso_id)
    lista_alunos = aluno.objects.filter(curso=curso_obj)
    hoje = date.today().strftime('%Y-%m-%d')

    if request.method == "POST":
        data_selecionada = request.POST.get('data_presenca')
        for a in lista_alunos:
            # Verifica se o checkbox do aluno foi marcado
            esta_presente = request.POST.get(f'aluno_{a.id}') == 'on'
            
            # Salva ou atualiza a presença
            Presenca.objects.update_or_create(
                aluno=a, 
                data=data_selecionada,
                defaults={'presente': esta_presente, 'curso': curso_obj}
            )
        return redirect('detalhe_curso', curso_id=curso_id)

    return render(request, 'controle_presenca.html', {
        'curso': curso_obj,
        'alunos': lista_alunos,
        'hoje': hoje
    })
