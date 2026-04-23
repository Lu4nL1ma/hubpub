from django.contrib import admin
from .models import divulgacao_agend, cursos, aluno, presenca, eixo_tematico

@admin.register(divulgacao_agend)
class DivulgacaoAgendAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na lista do Admin
    list_display = ('id','rede_social', 'tipo_post', 'data', 'legenda','hora', 'midia', 'ultima_publicacao')
    
    # Filtros na lateral direita
    list_filter = ('id','rede_social', 'tipo_post', 'data', 'legenda','ultima_publicacao')
    
    # Campo de busca (útil quando tiver muitos registros)
    search_fields = ('rede_social', 'legenda')
    
    # Ordenação padrão (mais recentes primeiro)
    ordering = ('-data',)


@admin.register(eixo_tematico)
class EixoTematicoAdmin(admin.ModelAdmin):
    # Campos que aparecerão na lista do painel
    list_display = ('id', 'eixo', 'data_criacao')
    
    # Adiciona uma barra de pesquisa pelo nome do eixo
    search_fields = ('eixo',)
    
    # Adiciona um filtro lateral por data
    list_filter = ('data_criacao',)
    
    # Ordenação padrão ao abrir o admin (do mais novo para o mais antigo)
    ordering = ('-id',)
    
    # Como 'data_criacao' tem auto_now_add=True, o Django o esconde por padrão.
    # Esta linha permite que você o veja dentro do formulário de edição (apenas leitura).
    readonly_fields = ('data_criacao',)

    # Configuração estética (opcional)
    fieldsets = (
        ('Informações do Eixo', {
            'fields': ('eixo',)
        }),
        ('Metadados', {
            'fields': ('data_criacao',),
            'classes': ('collapse',), # Deixa essa parte colapsada por padrão
        }),
    )


@admin.register(cursos)
class CursosAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na lista principal
    list_display = ('id','eixo','curso', 'turno', 'vagas', 'inscritos', 'data_inicio', 'professor', 'midia_feed', 'midia_post')
    
    # Filtros laterais para facilitar a navegação
    list_filter = ('turno', 'data_inicio', 'professor')
    
    # Campos que permitem busca (o campo professor usa __username para buscar pelo nome do usuário)
    search_fields = ('curso', 'legenda', 'professor__username')
    
    # Permite editar as vagas e inscritos diretamente na lista, sem entrar no registro
    list_editable = ('vagas', 'inscritos')
    
    # Organização do formulário de edição
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('curso', 'turno', 'professor')
        }),
        ('Datas e Vagas', {
            'fields': ('data_inicio', 'vagas', 'inscritos')
        }),
        ('Conteúdo e Mídia', {
            'fields': ('legenda', 'midia_post', 'midia_feed'),
            'classes': ('collapse',) # Deixa essa seção recolhida por padrão
        }),
    )

@admin.register(aluno)
class AlunoAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na lista de alunos
    list_display = ('nome', 'cpf', 'curso', 'data_matricula', 'ativo')
    
    # Campos que permitem clicar para entrar na edição
    list_display_links = ('nome', 'cpf')
    
    # Filtros laterais
    list_filter = ('curso', 'ativo', 'data_matricula')
    
    # Barra de busca (pesquisa por nome ou CPF)
    search_fields = ('nome', 'cpf')
    
    # Itens por página
    list_per_page = 20
    
    # Permite editar o status "ativo" diretamente na lista
    list_editable = ('ativo',)


@admin.register(presenca)
class PresencaAdmin(admin.ModelAdmin):
    # Colunas que aparecem na lista de presenças
    list_display = ('aluno', 'curso', 'data', 'status', 'presente')
    
    # Filtros para facilitar a busca por data e status
    list_filter = ('data', 'status', 'curso')
    
    # Permite pesquisar pelo nome do aluno diretamente na frequência
    search_fields = ('aluno__nome',)
    
    # Organiza por data mais recente
    ordering = ('-data',)