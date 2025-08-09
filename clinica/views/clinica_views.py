from decimal import Decimal
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_GET

from clinica.forms import (
    ClienteForm, AnimalForm, AgendamentoForm,
    RacaForm, EspecieForm, ProdutoServicoForm,
    AtendimentoClinicoForm, VacinaAplicadaFormSet,
)
from clinica.models import (
    Agendamento, Venda, ItemVenda, ProdutoServico,
    Cliente, Animal, Veterinario
)





# ============================ AUTENTICAÇÃO ============================

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


# ============================ PÁGINAS BÁSICAS ============================

@login_required(login_url='clinica:login')
def home_view(request):
    return render(request, 'clinica/home.html')


# ============================ CADASTROS ============================

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
        form = AnimalForm()
    return render(request, 'clinica/cadastros/cadastro_animal.html', {'form': form})


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


# ============================ AGENDAMENTO / CALENDÁRIO ============================

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


@require_GET
@login_required(login_url='clinica:login')
def eventos_json(request):
    eventos = []
    for ag in Agendamento.objects.select_related('animal', 'veterinario'):
        eventos.append({
            "title": f"{ag.animal.nome} - {ag.veterinario.nome if ag.veterinario else ''}",
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


# ============================ VENDAS / ITENS ============================

@login_required(login_url='clinica:login')
def nova_venda(request):
    return render(request, "clinica/nova_venda.html")


@login_required(login_url='clinica:login')
@require_http_methods(["POST"])
def salvar_venda(request):
    cliente_id = request.POST.get('cliente_id')
    descricao = request.POST.get('descricao', '')
    cliente = get_object_or_404(Cliente, id=cliente_id)

    venda = Venda.objects.create(cliente=cliente, descricao=descricao)

    produtos_ids = request.POST.getlist('produtos_id[]')
    quantidades = request.POST.getlist('produtos_quantidade[]')

    for i, pid in enumerate(produtos_ids):
        q = (quantidades[i] if i < len(quantidades) else '1') or '1'
        produto = get_object_or_404(ProdutoServico, id=pid)

        ItemVenda.objects.create(
            venda=venda,
            produto=produto,
            quantidade=Decimal(q.replace(',', '.')),
            preco_unitario=produto.preco,
        )

    messages.success(request, 'Venda salva com sucesso!')
    return redirect('clinica:nova_venda')


# ============================ ATENDIMENTO ============================

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
            messages.success(request, 'Atendimento registrado com sucesso!')
            return redirect('clinica:detalhes_animal', animal_id=animal.id)
        else:
            messages.error(request, 'Verifique os dados do atendimento.')
    else:
        form = AtendimentoClinicoForm(initial={'animal': animal})
        formset = VacinaAplicadaFormSet()

    return render(request, 'clinica/atendimento_clinico.html', {
        'form': form,
        'formset': formset,
        'animal': animal
    })

@require_GET
@login_required(login_url='clinica:login')
def buscar_animais(request):
    termo = (request.GET.get('q') or request.GET.get('term') or '').strip()
    tutor_id = request.GET.get('tutor_id')
    if not tutor_id:
        return JsonResponse([], safe=False)  # ou HttpResponseBadRequest

    qs = Animal.objects.select_related('cliente').filter(cliente_id=tutor_id)
    if termo:
        qs = qs.filter(nome__icontains=termo)
    qs = qs.order_by('nome')[:20]

    data = [{"id": a.id, "nome": a.nome, "especie": (a.especie.nome if getattr(a, "especie", None) else "")}
            for a in qs]
    return JsonResponse(data, safe=False)


# ============================ AUTOCOMPLETE / BUSCAS ============================

@require_GET
@login_required(login_url='clinica:login')
def buscar_clientes(request):
    termo = (request.GET.get('q') or request.GET.get('term') or '').strip()
    qs = Cliente.objects.all().order_by('nome')
    if termo:
        qs = qs.filter(nome__icontains=termo)
    data = []
    for c in qs[:15]:
        item = {"id": c.id, "nome": c.nome}
        doc = getattr(c, "cpf", None) or getattr(c, "cpf_cnpj", None)
        if doc: item["documento"] = doc
        data.append(item)
    return JsonResponse(data, safe=False)



@require_GET
@login_required(login_url='clinica:login')
def buscar_produtos_servicos(request):
    q = (request.GET.get('q') or '').strip()
    if not q:
        return JsonResponse([], safe=False)

    qs = (ProdutoServico.objects
          .filter(ativo=True, nome__icontains=q)
          .order_by("nome")[:20])

    data = []
    for p in qs:
        preco = float(p.preco) if p.preco is not None else 0.0
        tipo_val = getattr(p, "tipo_legivel", None)
        if callable(tipo_val):
            tipo_val = p.tipo_legivel
        if not tipo_val:
            tipo_val = getattr(p, "tipo", "")

        data.append({
            "id": p.id,
            "nome": p.nome,
            "preco": preco,
            "tipo": str(tipo_val or ""),
        })

    return JsonResponse(data, safe=False)

buscar_produtos = buscar_produtos_servicos


# ============================ VETERINÁRIOS ============================

@require_GET
@login_required(login_url='clinica:login')
def buscar_veterinarios(request):
    animal_id = request.GET.get("animal_id")
    qs = Veterinario.objects.filter(ativo=True).order_by("nome")

    data = [{"id": v.id, "nome": v.nome} for v in qs]
    return JsonResponse({"veterinarios": data})



buscar_produtos = buscar_produtos_servicos



@require_GET
@login_required(login_url='clinica:login')
def buscar_animais(request):
    termo = (request.GET.get('q') or request.GET.get('term') or '').strip()
    tutor_id = request.GET.get('tutor_id')
    if not tutor_id:
        return JsonResponse([], safe=False)  # ou HttpResponseBadRequest

    qs = Animal.objects.select_related('cliente').filter(cliente_id=tutor_id)
    if termo:
        qs = qs.filter(nome__icontains=termo)
    qs = qs.order_by('nome')[:20]

    data = [{"id": a.id, "nome": a.nome, "especie": (a.especie.nome if getattr(a, "especie", None) else "")}
            for a in qs]
    return JsonResponse(data, safe=False)

@require_GET
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