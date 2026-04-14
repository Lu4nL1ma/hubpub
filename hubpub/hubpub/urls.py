from django.contrib import admin
from django.urls import path, include
from app_hubpub.views import home, staff, agenda, forms_agenda, listar_cursos, cadastrar_curso, detalhe_curso, inserir_aluno, excluir_aluno, controle_presenca, gestao_alunos, MeuLoginView, historico_presenca
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('staff/', staff, name='staff'),
    path('login/', MeuLoginView.as_view(template_name='login.html'), name='login'),
    path('staff/agenda/', agenda, name='agenda'),
    path('staff/agenda/form-agenda/', forms_agenda, name='forms_agenda'),
    path('staff/agenda/deletar/<int:pk>/', views.deletar_agendamento, name='deletar_agendamento'),

    #inicia as urls de staff
    path('staff/cursos/', listar_cursos, name='painel_cursos'),
    path('staff/cursos/form/', cadastrar_curso, name='cadastrar_curso'),
    path('staff/cursos/<int:curso_id>/', detalhe_curso, name='detalhe_curso'),
    path('staff/cursos/<int:curso_id>/gerenciar-alunos', gestao_alunos, name='gestao_alunos'),
    path('staff/cursos/<int:curso_id>/gerenciar-alunos/inserir', inserir_aluno, name='inserir_aluno'),
    path('staff/cursos/<int:curso_id>/excluir-aluno/<int:aluno_id>/', excluir_aluno, name='excluir_aluno'),
    path('staff/cursos/<int:curso_id>/gerenciar-alunos/cntrl-pres', controle_presenca, name='controle_presenca'),
    path('staff/cursos/<int:curso_id>/gerenciar-alunos/hist-pres', historico_presenca, name='historico_presenca'),
    #end

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('admin/', admin.site.urls),
]

# Servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
