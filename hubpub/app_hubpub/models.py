from django.db import models
from django.utils import timezone

class divulgacao_agend(models.Model):
    #cursos
    curso = models.CharField(max_length=100, default='Não Especificado')

    # Default 'Geral' evita erro em registros antigos
    rede_social = models.CharField(max_length=100, default='Não Especificada')

    # Default 'Post' para preencher a coluna tipo_post
    tipo_post = models.CharField(max_length=100, default='Post Simples')
    
    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    legenda = models.TextField(blank=True, null=True, default='')

    # Campos de arquivo não costumam ter default de string, apenas null/blank
    midia = models.ImageField(upload_to='divulgacao/', null=True, blank=True)
    
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
    curso = models.CharField(max_length=100, default='Não Especificado')

    # Default 'Post' para preencher a coluna tipo_post
    turno = models.CharField(max_length=100, default='Não Definido')
    
    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    vagas = models.IntegerField(default=0, blank=True, null=True)

    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    inscritos = models.IntegerField(default=0, blank=True, null=True)
    
    # auto_now_add já define o default como "agora" na criação
    data_inicio = models.DateField(auto_now_add=False)

class aluno(models.Model):

    curso = models.CharField(max_length=150, default='Aluno sem Nome')

    nome = models.CharField(max_length=150, default='Aluno sem Nome')

    email = models.EmailField(max_length=150, default='contato@exemplo.com')
    
    cpf = models.CharField(max_length=14, default='000.000.000-00')
    
    data_nascimento = models.DateField(default=timezone.now)
    
    ativo = models.BooleanField(default=True)

    data_matricula = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # Linha 67 (com 8 espaços ou 2 TABs de recuo)
        nome_curso = self.curso.curso if self.curso else "Sem Curso"
        return f"{self.nome} - {nome_curso}"
        
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"