from django.db import models
from django.contrib.auth.models import User
from clinica.models import Cliente, ProdutoServico

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    total = models.FloatField()
    qtd_total = models.PositiveIntegerField()
    status = models.CharField(
        default="C",
        max_length=1,
        choices=(
            ('A', 'Aprovado'),
            ('C', 'Criado'),
            ('R', 'Reprovado'),
            ('P', 'Pendente'),
            ('E', 'Enviado'),
            ('F', 'Finalizado'),
        )
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente.nome}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(ProdutoServico, on_delete=models.CASCADE)
    preco = models.FloatField()
    quantidade = models.PositiveIntegerField()
    desconto = models.FloatField(default=0.0)

    def subtotal(self):
        return (self.preco - self.desconto) * self.quantidade

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} (Pedido #{self.pedido.pk})'
    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'