from django import forms
from clinica.models import Cliente, ProdutoServico
from .models import Pedido, ItemPedido
from django.forms import inlineformset_factory


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente']  # total e qtd_total serão calculados na view


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade', 'desconto']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min': '1', 'value': '1'}),
            'desconto': forms.NumberInput(attrs={'step': '0.01', 'value': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = ProdutoServico.objects.filter(ativo=True)
        self.fields['produto'].label_from_instance = lambda obj: f"{obj.nome} - R$ {obj.preco}"


# Formset para múltiplos itens em um único pedido
ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    can_delete=True
)


class ItemVendaForm(forms.Form):
    produto = forms.ModelChoiceField(queryset=ProdutoServico.objects.all())
    quantidade = forms.IntegerField(min_value=1, initial=1)

class NovaVendaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())