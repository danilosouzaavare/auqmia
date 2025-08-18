# clinica/views/clinica_views.py
from decimal import Decimal
import datetime
from io import BytesIO

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_GET
from django.template.loader import get_template
from django.templatetags.static import static
from django.db import transaction

from xhtml2pdf import pisa

from clinica.forms import (
    ClienteForm, AnimalForm, AgendamentoForm,
    RacaForm, EspecieForm, ProdutoServicoForm,
    AtendimentoClinicoForm, VacinaAplicadaFormSet, VeterinarioForm
)
from clinica.models import (
    Agendamento, Venda, ItemVenda, ProdutoServico,
    Cliente, Animal, Veterinario, AtendimentoClinico
)

# Alias (se o atendimento "oficial" é AtendimentoClinico)
Atendimento = AtendimentoClinico


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
def cadastro_veterinario_view(request):
    if request.method == 'POST':
        form = VeterinarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veterinário cadastrado com sucesso!')
            return redirect('clinica:cadastro_veterinario')
    else:
        form = VeterinarioForm()
    return render(request, 'clinica/cadastros/cadastro_veterinario.html', {'form': form})


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
        if doc:
            item["documento"] = doc
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

buscar_produtos = buscar_produtos_servicos  # alias opcional


@require_GET
@login_required(login_url='clinica:login')
def buscar_animais(request):
    termo = (request.GET.get('q') or request.GET.get('term') or '').strip()
    tutor_id = request.GET.get('tutor_id')
    if not tutor_id:
        return JsonResponse([], safe=False)

    qs = Animal.objects.select_related('cliente').filter(cliente_id=tutor_id)
    if termo:
        qs = qs.filter(nome__icontains=termo)
    qs = qs.order_by('nome')[:20]

    data = [{"id": a.id, "nome": a.nome, "especie": (a.especie.nome if getattr(a, "especie", None) else "")}
            for a in qs]
    return JsonResponse(data, safe=False)


# ============================ VETERINÁRIOS ============================

@require_GET
@login_required(login_url='clinica:login')
def buscar_veterinarios(request):
    qs = Veterinario.objects.filter(ativo=True).order_by("nome")
    data = [{"id": v.id, "nome": v.nome} for v in qs]
    return JsonResponse({"veterinarios": data})


# ============================ BUSCA PARA TELAS LEGADAS ============================

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


# ============================ PDF DO ATENDIMENTO ============================

def _render_to_pdf(template_src, context):
    """Renderiza um template HTML em PDF usando xhtml2pdf e retorna bytes."""
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=BytesIO(html.encode('utf-8')), dest=result, encoding='utf-8')
    if pisa_status.err:
        return None
    return result.getvalue()


def _collect_vacinas(atendimento):
    """
    Retorna uma lista com as vacinas aplicadas ligadas ao atendimento.
    Estratégia:
      1) nomes explícitos comuns
      2) introspecção de relacionamentos reversos contendo 'vacina'/'aplic'
      3) itens do atendimento que pareçam vacina (fallback)
    """
    # 1) nomes comuns
    explicit_rel_names = [
        'vacinas', 'vacinas_aplicadas', 'vacinas_atendimento',
        'aplicacoes_vacina', 'aplicacao_vacinas', 'aplicacao_de_vacinas',
        'aplicacoes', 'aplicacao_set', 'aplicacoes_set',
        # nomes gerados automaticamente
        'vacinaaplicada_set', 'vacina_aplicada_set', 'vacinasaplicadas_set',
    ]
    for name in explicit_rel_names:
        rel = getattr(atendimento, name, None)
        if hasattr(rel, 'all'):
            try:
                qs = list(rel.all())
            except TypeError:
                # caso seja M2M sem .all(), ignora
                qs = []
            if qs:
                return qs

    # 2) introspecção de reversos
    try:
        for f in atendimento._meta.get_fields():
            if getattr(f, 'auto_created', False) and hasattr(f, 'get_accessor_name'):
                accessor = f.get_accessor_name()  # ex.: 'vacinaaplicada_set'
                if accessor and any(tok in accessor.lower() for tok in ('vacina', 'aplic')):
                    manager = getattr(atendimento, accessor, None)
                    if hasattr(manager, 'all'):
                        qs = list(manager.all())
                        if qs:
                            return qs
    except Exception:
        pass

    # 3) fallback: itens do atendimento
    itens = getattr(atendimento, 'itens', None)
    if hasattr(itens, 'all'):
        # tenta por flag
        try:
            qs = list(itens.filter(tipo='vacina'))
            if qs:
                return qs
        except Exception:
            pass
        # heurística por nome
        only_vacinas = []
        for it in list(itens.all()):
            nome = getattr(it, 'nome', None) or getattr(getattr(it, 'produto', None), 'nome', None) or ''
            if isinstance(nome, str) and 'vacina' in nome.lower():
                only_vacinas.append(it)
        if only_vacinas:
            return only_vacinas

    return []


@login_required(login_url='clinica:login')
def atendimento_resumo_pdf(request, pk):
    atendimento = get_object_or_404(Atendimento, pk=pk)

    # Animal / Tutor / Veterinário
    animal = getattr(atendimento, 'animal', None)
    tutor = (getattr(animal, 'tutor', None) if animal else None) or (getattr(animal, 'cliente', None) if animal else None)
    veterinario = getattr(atendimento, 'veterinario', None)

    # Vacinas
    vacinas_list = _collect_vacinas(atendimento)

    # Logo absoluto (opcional)
    logo_url = request.build_absolute_uri(static('global/img/logo.png'))

    context = {
        'atendimento': atendimento,
        'animal': animal,
        'tutor': tutor,
        'veterinario': veterinario,
        'logo_url': logo_url,

        # campos de texto / datas (ajuste se o seu model tiver outros nomes)
        'data_hora': getattr(atendimento, 'data_hora', None),
        'anamnese': getattr(atendimento, 'anamnese', ''),
        'sintomas': getattr(atendimento, 'sintomas', ''),
        'diagnostico': getattr(atendimento, 'diagnostico', ''),
        'tratamento': getattr(atendimento, 'tratamento', ''),
        'exames_solicitados': getattr(atendimento, 'exames_solicitados', ''),
        'orientacoes': getattr(atendimento, 'orientacoes', ''),

        # retorno: mantemos 'retorno' e o template trata outros nomes, se precisar
        'retorno': getattr(atendimento, 'retorno', None),

        # vacinas
        'vacinas_list': vacinas_list,

        # dados da clínica (exemplo)
        'clinica_nome': 'Clinica Auqmia',
        'clinica_endereco': 'R. Voluntários de Avaré, 878 - Centro, Avaré - SP, 18700-240',
        'clinica_contato': '(14) 3731-1520',
    }

    # !!! IMPORTANTE: caminho do template confere com a pasta onde você salvou o HTML
    pdf_bytes = _render_to_pdf('clinica/resumo_pdf.html', context)
    if not pdf_bytes:
        return HttpResponse('Erro ao gerar o PDF.', status=500)

    filename = f"resumo_atendimento_{atendimento.pk}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ============================ ATENDIMENTO ============================

@login_required(login_url='clinica:login')
def atendimento_novo(request, animal_id, vet_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    cliente_id = getattr(animal, 'tutor_id', None) or getattr(animal, 'cliente_id', None)
    if not cliente_id:
        messages.error(request, 'Não foi possível identificar o tutor/cliente do animal.')
        return redirect('clinica:lista_agendamentos')

    atendimento = None

    if request.method == 'POST':
        data = request.POST.copy()
        data['animal'] = str(animal_id)
        data['veterinario'] = str(vet_id)
        if not data.get('data_hora'):
            data['data_hora'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        form = AtendimentoClinicoForm(data, request.FILES)
        formset = VacinaAplicadaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                atendimento = form.save(commit=False)
                atendimento.animal_id = animal_id
                atendimento.veterinario_id = vet_id
                if hasattr(atendimento, 'cliente_id'):
                    atendimento.cliente_id = cliente_id
                if not getattr(atendimento, 'data_hora', None):
                    atendimento.data_hora = timezone.now()
                atendimento.save()

                # Recria o formset com instance para vincular os filhos ao atendimento salvo
                formset = VacinaAplicadaFormSet(request.POST, instance=atendimento)

                if formset.is_valid():
                    objs = formset.save(commit=False)
                    for obj in objs:
                        if hasattr(obj, 'animal_id') and not obj.animal_id:
                            obj.animal_id = animal_id
                        if hasattr(obj, 'cliente_id') and not obj.cliente_id:
                            obj.cliente_id = cliente_id
                        if hasattr(obj, 'veterinario_id') and not obj.veterinario_id:
                            obj.veterinario_id = vet_id
                        if hasattr(obj, 'atendimento_id') and not obj.atendimento_id:
                            obj.atendimento_id = atendimento.pk
                        obj.save()

                    # Deleções marcadas
                    for obj in formset.deleted_objects:
                        obj.delete()

                    formset.save_m2m()
                else:
                    raise ValueError(formset.errors)

            messages.success(request, 'Atendimento registrado com sucesso!')
            return redirect('clinica:atendimento_resumo_pdf', pk=atendimento.pk)

        # Erros de validação
        detalhes = []
        if form.errors:
            for campo, erros in form.errors.items():
                detalhes.append(f"[form] {campo}: {', '.join(map(str, erros))}")
        if form.non_field_errors():
            detalhes.append(f"[form] non_field: {', '.join(map(str, form.non_field_errors()))}")
        if formset.errors:
            for idx, f in enumerate(formset.forms):
                if f.errors:
                    for campo, erros in f.errors.items():
                        detalhes.append(f"[vacina {idx}] {campo}: {', '.join(map(str, erros))}")
        if formset.non_form_errors():
            detalhes.append(f"[formset] non_form: {', '.join(map(str, formset.non_form_errors()))}")

        messages.error(request, "Verifique os dados do atendimento: " + " | ".join(detalhes) if detalhes else
                       "Verifique os dados do atendimento.")

    else:
        form = AtendimentoClinicoForm(initial={'animal': animal})
        formset = VacinaAplicadaFormSet()

    return render(request, 'clinica/atendimento_clinico.html', {
        'form': form,
        'formset': formset,
        'animal': animal,
        'vet_id': vet_id,
        'atendimento': atendimento,
    })


@login_required(login_url='clinica:login')
def atendimento_novo_qs(request, animal_id):
    """
    Compatibilidade com o formato antigo:
    /atendimento/novo/<animal_id>/?vet=<vet_id>
    Redireciona para /atendimento/novo/<animal_id>/<vet_id>/
    """
    vet = request.GET.get('vet')
    if not vet or not str(vet).isdigit():
        return HttpResponseBadRequest("Parâmetro ?vet= é obrigatório e deve ser numérico.")
    return redirect('clinica:atendimento_novo', animal_id=animal_id, vet_id=int(vet))
