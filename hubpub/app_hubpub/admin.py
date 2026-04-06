from django.contrib import admin
from .models import divulgacao_agend, cursos

@admin.register(divulgacao_agend)
class DivulgacaoAgendAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na lista do Admin
    list_display = ('id','rede_social', 'tipo_post', 'data', 'legenda','hora', 'ultima_publicacao')
    
    # Filtros na lateral direita
    list_filter = ('id','rede_social', 'tipo_post', 'data', 'legenda','ultima_publicacao')
    
    # Campo de busca (útil quando tiver muitos registros)
    search_fields = ('rede_social', 'legenda')
    
    # Ordenação padrão (mais recentes primeiro)
    ordering = ('-data',)

@admin.register(cursos)
class CursosAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na listagem principal
    list_display = ('id', 'curso', 'turno', 'data_inicio')
    
    # Filtros laterais para facilitar a busca
    list_filter = ('turno', 'data_inicio')
    
    # Campos que permitem clicar para entrar na edição
    list_display_links = ('id', 'curso')
    
    # Barra de busca (pesquisa pelo nome do curso ou turno)
    search_fields = ('curso', 'turno')
    
    # Ordenação padrão (mais recentes primeiro)
    ordering = ('-data_inicio',)