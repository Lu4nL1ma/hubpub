from django.db import models
from django.utils import timezone

class divulgacao_agend(models.Model):
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
        return self.rede_social


class  cursos(models.Model):
    # Default 'Geral' evita erro em registros antigos
    curso = models.CharField(max_length=100, default='Não Especificada')

    # Default 'Post' para preencher a coluna tipo_post
    turno = models.CharField(max_length=100, default='Post Simples')
    
    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    vagas = models.TextField(blank=True, null=True, default='')

    # blank/null já lidam com o "vazio", mas o default='' garante consistência
    inscritos = models.TextField(blank=True, null=True, default='')
    
    # auto_now_add já define o default como "agora" na criação
    data_inicio = models.DateField(auto_now_add=False)
