from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import date

class divulgacao_agend(models.Model):
    #cursos
    curso = models.CharField(max_length=300, default='')

    # Default 'Geral' evita erro em registros antigos
    rede_social = models.CharField(max_length=100, default='')

    # Default 'Post' para preencher a coluna tipo_post
    tipo_post = models.CharField(max_length=100, default='')
    
    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    legenda = models.TextField(blank=True, null=True, default='')

    # Campos de arquivo não costumam ter default de string, apenas null/blank
    midia = models.CharField(max_length=100, default='Não Especificado')
    
    # auto_now_add já define o default como "agora" na criação
    data = models.DateField(auto_now_add=False)

    # Para CharField de hora, defini um valor padrão de texto
    hora = models.CharField(max_length=100, default='00:00')

    #para registrar ultima publicacao
    ultima_publicacao = models.DateField(null=True, blank=True, default=None)

    def __str__(self):
        # Corrigido para retornar um campo que existe (rede_social)
        return f"{self.curso} - {self.rede_social} - {self.tipo_post}"


class  cursos(models.Model):
    # Default 'Geral' evita erro em registros antigos
    curso = models.CharField(max_length=100, default='')

    # Default 'Post' para preencher a coluna tipo_post
    turno = models.CharField(max_length=100, default='')
    
    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    vagas = models.IntegerField(default=0, blank=True, null=True)

    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    inscritos = models.IntegerField(default=0, blank=True, null=True)
    
    # auto_now_add já define o default como "agora" na criação
    data_inicio = models.DateField(auto_now_add=False)

    # Campos de arquivo não costumam ter default de string, apenas null/blank
    midia_post = models.ImageField(upload_to='divulgacao/story', null=True, blank=True)

    # Campos de arquivo não costumam ter default de string, apenas null/blank
    midia_feed = models.ImageField(upload_to='divulgacao/feed', null=True, blank=True)

    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    legenda = models.TextField(blank=True, null=True, default='')

    # professor 
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Professor Responsável")

    def __str__(self):
        return self.curso

class aluno(models.Model):
    # CORREÇÃO: Transformando em ForeignKey para ligar com o model 'cursos'
    curso = models.ForeignKey(
        'cursos', 
        on_delete=models.CASCADE, 
        related_name='alunos_matriculados',
        null=True, 
        blank=True
    )

    nome = models.CharField(max_length=150, default='')
    email = models.EmailField(max_length=150, default='')
    cpf = models.CharField(max_length=14, default='')
    data_nascimento = models.DateField(default=timezone.now)
    ativo = models.BooleanField(default=True)
    data_matricula = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # Agora que é ForeignKey, podemos acessar o campo 'curso' do model ligado
        # Se o campo de nome no seu model 'cursos' se chamar 'curso', fica assim:
        nome_do_curso = self.curso.curso if self.curso else "Sem Curso"
        return f"{self.nome} - {nome_do_curso}"
        
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

class presenca(models.Model):
    STATUS_CHOICES = [
        ('P', 'Presente'),
        ('A', 'Ausente'),
        ('J', 'Justificado'),
    ]

    aluno = models.ForeignKey('aluno', on_delete=models.CASCADE, related_name='frequencias')
    curso = models.ForeignKey('cursos', on_delete=models.CASCADE, related_name='chamadas')
    data = models.DateField(default=date.today)
    presente = models.BooleanField(default=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    observacao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_hubpub_presenca' # Força o nome da tabela no MySQL
        unique_together = ('aluno', 'curso', 'data')

    def __str__(self):
        return f"{self.aluno.nome} - {self.data}"