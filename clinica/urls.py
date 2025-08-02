from django.conf import settings
from django.urls import path, include
from . import views
from django.views.generic import TemplateView

app_name = 'clinica'

urlpatterns = [
    path('', views.login_view, name='login'),
    #path('home/', views.home_view, name='home_view'),
    path('cadastro_cliente/', views.cadastro_cliente_view, name='cadastro_cliente'),
    path('cadastro_animal/', views.cadastro_animal_view, name='cadastro_animal'),
    path('agendamento/novo/', views.criar_agendamento, name='criar_agendamento'),
    path('agendamentos/', views.lista_agendamentos, name='lista_agendamentos'),
    path('calendario/', views.calendario_view, name='home_view'),
    path('api/agendamentos/', views.eventos_json, name='eventos_json'),
    path('cadastro_raca/', views.cadastro_raca_view, name='cadastro_raca'),
    path('cadastro_especie/', views.cadastro_especie_view, name='cadastro_especie'),
    path('cadastro_produto_servico/', views.cadastro_produto_view, name='cadastro_produto_servico'),
    path('user/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('buscar-clientes/', views.buscar_clientes, name='buscar_clientes'),
    path('clientes/busca/', views.pagina_busca_clientes, name='pagina_busca_clientes'),


    path('produtos/buscar/', views.buscar_produtos, name='buscar_produtos'),

    path('vendas/salvar/', views.salvar_venda, name='salvar_venda'),

    path('vendas/nova/', views.nova_venda, name='nova_venda'),

    path('buscar-tutores/', views.buscar_tutores, name='buscar_tutores'),
    path('ajax/buscar-animais/', views.buscar_animais, name='buscar_animais'),
    


    path('atendimento/novo/<int:animal_id>/', views.atendimento_novo, name='atendimento_novo'),
    path('ajax/buscar-animais-atendimento/', views.buscar_animais_para_atendimento, name='buscar_animais_para_atendimento'),
    path('atendimento/selecionar/', TemplateView.as_view(template_name='clinica/selecionar_animal.html'), name='selecionar_animal'),

]





# Ativa o Django Debug Toolbar apenas no modo DEBUG
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]


