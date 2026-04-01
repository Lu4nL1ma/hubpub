from django.contrib import admin
from .models import divulgacao_agend

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