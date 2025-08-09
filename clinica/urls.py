from django.conf import settings
from django.urls import path, include
from clinica.views import clinica_views as views  # importa direto o módulo certo
from django.views.generic import TemplateView


app_name = 'clinica'

urlpatterns = [
    # Autenticação / Home
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home_view'),

    # Cadastros
    path('cadastro_cliente/', views.cadastro_cliente_view, name='cadastro_cliente'),
    path('cadastro_animal/', views.cadastro_animal_view, name='cadastro_animal'),
    path('cadastro_raca/', views.cadastro_raca_view, name='cadastro_raca'),
    path('cadastro_especie/', views.cadastro_especie_view, name='cadastro_especie'),
    path('cadastro_produto_servico/', views.cadastro_produto_view, name='cadastro_produto_servico'),

    # Agendamentos / Calendário
    path('agendamento/novo/', views.criar_agendamento, name='criar_agendamento'),
    path('agendamentos/', views.lista_agendamentos, name='lista_agendamentos'),
    path('calendario/', views.calendario_view, name='calendario'),
    path('api/agendamentos/', views.eventos_json, name='eventos_json'),

    # APIs de autocomplete (usadas pela nova venda)
    path('api/clientes/buscar/', views.buscar_clientes, name='buscar_clientes'),
    
    path('api/itens/buscar/', views.buscar_produtos_servicos, name='buscar_produtos_servicos'),
    path("api/animais/buscar/", views.buscar_animais, name="buscar_animais"),
    

    # Vendas
    path('vendas/nova/', views.nova_venda, name='nova_venda'),
    path('vendas/salvar/', views.salvar_venda, name='salvar_venda'),

    # Atendimento
    path('atendimento/novo/<int:animal_id>/', views.atendimento_novo, name='atendimento_novo'),

    # (Opcional/legado) Seleção e busca p/ telas antigas
    path('ajax/buscar-animais-atendimento/', views.buscar_animais_para_atendimento, name='buscar_animais_para_atendimento'),
    path('atendimento/selecionar/', TemplateView.as_view(template_name='clinica/selecionar_animal.html'), name='selecionar_animal'),

    # Veterinários
    path('buscar_veterinarios/', views.buscar_veterinarios, name='buscar_veterinarios'),
]

# Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

