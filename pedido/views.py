from django.shortcuts import render, redirect
from django.db import transaction
from .models import Pedido, ItemPedido
from .forms import PedidoForm, ItemPedidoFormSet


def criar_pedido(request):
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        formset = ItemPedidoFormSet(request.POST)

        if pedido_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                pedido = pedido_form.save(commit=False)
                pedido.total = 0
                pedido.qtd_total = 0
                pedido.save()

                total = 0
                qtd_total = 0

                itens = formset.save(commit=False)
                for item in itens:
                    item.pedido = pedido
                    item.preco = item.produto.preco  # garante que o preço vem do produto
                    item.save()
                    total += (item.preco - item.desconto) * item.quantidade
                    qtd_total += item.quantidade

                pedido.total = total
                pedido.qtd_total = qtd_total
                pedido.save()

                return redirect('pedido_sucesso')  # você pode mudar esse destino
    else:
        pedido_form = PedidoForm()
        formset = ItemPedidoFormSet()

    return render(request, 'pedido/criar_pedido.html', {
        'pedido_form': pedido_form,
        'formset': formset,
    })


def pedido_sucesso(request):
    return HttpResponse("<h1>Pedido realizado com sucesso!</h1>")




def nova_venda(request):
    if request.method == 'POST':
        venda_form = NovaVendaForm(request.POST)
        produtos_ids = request.POST.getlist('produto')
        quantidades = request.POST.getlist('quantidade')

        if venda_form.is_valid():
            cliente = venda_form.cleaned_data['cliente']
            total = 0
            qtd_total = 0
            itens = []

            for pid, qtd in zip(produtos_ids, quantidades):
                produto = ProdutoServico.objects.get(id=pid)
                qtd = int(qtd)
                preco = produto.valor
                total += preco * qtd
                qtd_total += qtd
                itens.append((produto, qtd, preco))

            pedido = Pedido.objects.create(
                usuario=request.user,
                total=total,
                qtd_total=qtd_total,
                status='C',
            )

            for produto, qtd, preco in itens:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto.nome,
                    produto_id=produto.id,
                    preco=preco,
                    quantidade=qtd,
                )

            return redirect('pedido_sucesso')

    else:
        venda_form = NovaVendaForm()
        item_form = ItemVendaForm()

    return render(request, 'pedido/nova_venda.html', {
        'venda_form': venda_form,
        'item_form': item_form,
    })

