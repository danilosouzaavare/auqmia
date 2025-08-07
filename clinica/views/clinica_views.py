from clinica.forms import * 
from django.shortcuts import render, redirect
from django.http import JsonResponse
from clinica.models import Agendamento
import datetime
import django.contrib.messages as messages
from decimal import Decimal
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required



from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from clinica.models import Venda, ItemVenda, ProdutoServico, Cliente, Animal, Veterinario
from django.views.decorators.http import require_GET


def login_view(request):
    return render(request, 'clinica/login.html')

@login_required(login_url='clinica:login')
def home_view(request):
    return render(request, 'clinica/home.html')

@login_required(login_url='clinica:login')
def cadastro_cliente_view(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clinica:cadastro_cliente')
    else:
        form = ClienteForm()
    
    return render(request, 'clinica/cadastros/cadastro_cliente.html', {'form': form})


@login_required(login_url='clinica:login')
def cadastro_animal_view(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal cadastrado com sucesso!')
            return redirect('clinica:cadastro_animal')
    else:
        form = AnimalForm() # type: ignore

    return render(request, 'clinica/cadastros/cadastro_animal.html', {'form': form})

@login_required(login_url='clinica:login')
def criar_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
            agendamentos = Agendamento.objects.order_by('data_hora')
            return render(request, 'clinica/lista_agendamentos.html', {'agendamentos': agendamentos})
    else:
        form = AgendamentoForm()

    return render(request, 'clinica/agendamento_form.html', {'form': form})

@login_required(login_url='clinica:login')
def lista_agendamentos(request):
    agendamentos = Agendamento.objects.order_by('data_hora')
    return render(request, 'clinica/lista_agendamentos.html', {'agendamentos': agendamentos})


def eventos_json(request):
    eventos = []
    for ag in Agendamento.objects.select_related('animal', 'veterinario'):
        eventos.append({
            "title": f"{ag.animal.nome} - {ag.veterinario.nome}", # type: ignore
            "start": ag.data_hora.isoformat(),
            "end": ag.data_hora.isoformat(),
            "color": (
                "#4CAF50" if ag.status == 'A'
                else "#F44336" if ag.status == 'C'
                else "#616161"
            )
        })
    return JsonResponse(eventos, safe=False)

@login_required(login_url='clinica:login')
def calendario_view(request):
    return render(request, 'clinica/calendario.html')


@login_required(login_url='clinica:login')
def cadastro_raca_view(request):
    if request.method == 'POST':
        form = RacaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Raça cadastrada com sucesso!')
            return redirect('clinica:cadastro_raca')

    else:
        form = RacaForm()

    return render(request, 'clinica/cadastros/cadastro_raca.html', {'form': form})

@login_required(login_url='clinica:login')
def cadastro_especie_view(request):
    if request.method == 'POST':
        form = EspecieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Espécie cadastrada com sucesso!')
            return redirect('clinica:cadastro_especie')
    else:
        form = EspecieForm()

    return render(request, 'clinica/cadastros/cadastro_especie.html', {'form': form})

@login_required(login_url='clinica:login')
def buscar_clientes(request):
    termo = request.GET.get('q', '')
    resultados = Cliente.objects.filter(nome__icontains=termo).values('id', 'nome')[:10]
    return JsonResponse(list(resultados), safe=False)


@login_required(login_url='clinica:login')
def pagina_busca_clientes(request):
    return render(request, 'clinica/cadastros/busca_cliente.html')


@require_GET
def buscar_produtos(request):
    q = request.GET.get('q', '')
    produtos = ProdutoServico.objects.filter(nome__icontains=q, ativo=True)[:10]
    data = [
        {'id': p.id, 'nome': p.nome, 'preco': str(p.preco)}
        for p in produtos
    ]
    print('Preço é', data)
    # Retorna os dados em formato JSON
    return JsonResponse(data, safe=False)


@login_required(login_url='clinica:login')
@require_http_methods(["POST"])
def salvar_venda(request):
    cliente_id = request.POST.get('cliente_id')
    descricao = request.POST.get('descricao', '')

    cliente = get_object_or_404(Cliente, id=cliente_id)
    venda = Venda.objects.create(cliente=cliente, descricao=descricao)

    produtos_ids = request.POST.getlist('produtos[][pk]')
    quantidades = request.POST.getlist('produtos[][quantidade]')
    precos = request.POST.getlist('produtos[][preco]')

    # Os nomes dos inputs do form gerado pelo JS são arrays, mas Django pode ter dificuldade com eles,
    # talvez seja melhor ajustar os names para algo tipo produtos-id[], produtos-quantidade[] etc.
    # Vou adaptar abaixo para facilitar:

    produtos_ids = request.POST.getlist('produtos_id[]')
    quantidades = request.POST.getlist('produtos_quantidade[]')
    precos = request.POST.getlist('produtos_preco[]')

    for pid, q in zip(produtos_ids, quantidades):
        produto = get_object_or_404(ProdutoServico, id=pid)
        ItemVenda.objects.create(
        venda=venda,
        produto=produto,
        quantidade=Decimal(q.replace(',', '.')),
        preco_unitario=produto.preco,
    )
   

    return redirect('clinica:pagina_de_vendas')

@login_required(login_url='clinica:login')
def nova_venda(request):
    return render(request, 'clinica/nova_venda.html')

@login_required(login_url='clinica:login')
def cadastro_produto_view(request):
    if request.method == 'POST':
        form = ProdutoServicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto/Serviço cadastrado com sucesso!')
            return redirect('clinica:cadastro_produto_servico')
    else:
        form = ProdutoServicoForm()

    return render(request, 'clinica/cadastros/cadastro_produto.html', {'form': form})


@login_required(login_url='clinica:login')
def buscar_tutores(request):
    """
    View para autocomplete de tutor (Cliente).
    Retorna até 10 clientes cujo nome contém o termo buscado (case-insensitive).
    """
    termo = request.GET.get('q', '')
    clientes = Cliente.objects.filter(nome__icontains=termo).order_by('nome')[:10]
    data = [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "telefone": c.telefone,
            "email": c.email,
        }
        for c in clientes
    ]
    return JsonResponse(data, safe=False)


@login_required(login_url='clinica:login')
def buscar_animais(request):
    termo = request.GET.get('q', '')
    tutor_id = request.GET.get('tutor_id')
    if not tutor_id:
        return JsonResponse([], safe=False)
    animais = Animal.objects.filter(
        cliente_id=tutor_id,
        nome__icontains=termo
    ).order_by('nome')[:10]
    data = [
        {
            "id": a.id,
            "nome": a.nome,
            "especie": a.especie.nome if a.especie else "",
            
        }
     
        for a in animais

    

    ]
    return JsonResponse(data, safe=False)


@login_required(login_url='clinica:login')
def atendimento_novo(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    if request.method == 'POST':
        form = AtendimentoClinicoForm(request.POST)
        formset = VacinaAplicadaFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            atendimento = form.save(commit=False)
            atendimento.animal = animal
            atendimento.save()
            formset.instance = atendimento
            formset.save()
            return redirect('clinica:detalhes_animal', animal_id=animal.id)
    else:
        form = AtendimentoClinicoForm(initial={'animal': animal})
        formset = VacinaAplicadaFormSet()
    return render(request, 'clinica/atendimento_clinico.html', {
        'form': form,
        'formset': formset,
        'animal': animal
    })



@login_required(login_url='clinica:login')
def buscar_animais_para_atendimento(request):
    termo = request.GET.get('term', '')
    animais = Animal.objects.filter(nome__icontains=termo)[:10]
    resultados = []
    for animal in animais:
        resultados.append({
            'id': animal.id,
            'label': f"{animal.nome} ({animal.cliente.nome})",
            'value': animal.nome,
        })
    return JsonResponse(resultados, safe=False)




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('clinica:home_view')
        else:
            messages.error(request, 'Login inválido. Por favor, tente novamente.')
    else:
        form = AuthenticationForm()

    return render(request, 'clinica/login.html', {'form': form})


def logout_view(request):
    auth.logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('clinica:login')






def buscar_veterinarios(request):
    animal_id = request.GET.get("animal_id")
    # por enquanto, regra simples: todos ativos
    qs = Veterinario.objects.filter(ativo=True).order_by("nome")
    # se quiser filtrar por espécie do animal no futuro, você tem animal.especie disponível aqui
    # try:
    #     animal = Animal.objects.get(pk=animal_id)
    #     qs = qs.filter(especialidade__icontains=animal.especie.nome)
    # except (Animal.DoesNotExist, AttributeError, TypeError):
    #     pass

    data = [{"id": v.id, "nome": v.nome} for v in qs]  # mostra só o nome
    return JsonResponse({"veterinarios": data})