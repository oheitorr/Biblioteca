from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.index, name='index'),

    # Vícios
    path('vicio/criar/', views.criar_vicio, name='criar_vicio'),
    path('vicio/<int:vicio_id>/editar/', views.editar_vicio, name='editar_vicio'),
    path('vicio/<int:vicio_id>/deletar/', views.deletar_vicio, name='deletar_vicio'),

    # Hábitos
    path('habitos/', views.habitos_view, name='habitos'),
    path('habitos/<int:habito_id>/deletar/', views.deletar_habito, name='deletar_habito'),

    # Metas
    path('metas/', views.metas_view, name='metas'),
    path('metas/<int:meta_id>/concluir/', views.concluir_meta, name='concluir_meta'),
    path('metas/<int:meta_id>/deletar/', views.deletar_meta, name='deletar_meta'),

    # Recaídas
    path('recaidas/', views.recaidas_view, name='recaidas'),
    path('recaidas/<int:recaida_id>/deletar/', views.deletar_recaida, name='deletar_recaida'),

    # Gatilhos
    path('gatilhos/', views.gatilhos_view, name='gatilhos'),
    path('gatilhos/<int:gatilho_id>/deletar/', views.deletar_gatilho, name='deletar_gatilho'),

    # Registro de gatilhos
    path('registro-gatilhos/', views.registro_gatilhos_view, name='registro_gatilhos'),
    path('registro-gatilhos/<int:registro_id>/deletar/', views.deletar_registro_gatilho, name='deletar_registro_gatilho'),

    # Rotinas
    path('rotinas/', views.rotinas_view, name='rotinas'),
    path('rotinas/<int:rotina_id>/deletar/', views.deletar_rotina, name='deletar_rotina'),

    # Tarefas
    path('tarefas/', views.tarefas_view, name='tarefas'),
    path('tarefas/<int:tarefa_id>/concluir/', views.concluir_tarefa, name='concluir_tarefa'),
    path('tarefas/<int:tarefa_id>/deletar/', views.deletar_tarefa, name='deletar_tarefa'),

    # Substituições
    path('substituicoes/', views.substituicoes_view, name='substituicoes'),
    path('substituicoes/<int:substituicao_id>/deletar/', views.deletar_substituicao, name='deletar_substituicao'),

    # Streaks e progressos (somente leitura, calculados)
    path('streaks/', views.streaks_view, name='streaks'),
    path('progressos/', views.progressos_view, name='progressos'),

    # Demais páginas
    path('categorias/', views.categorias_view, name='categorias'),
    path('conquistas/', views.conquistas_view, name='conquistas'),
    path('recompensas/', views.recompensas_view, name='recompensas'),
    path('frases/', views.frases_view, name='frases'),
    path('historicos/', views.historicos_view, name='historicos'),
    path('perfis/', views.perfis_view, name='perfis'),
]