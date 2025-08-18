from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from typing import Optional



# Create your models here.
from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='O CPF deve conter exatamente 11 números.'
            )
        ]
    )
    endereco = models.CharField(max_length=255, verbose_name='Endereço')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    telefone_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone 2')
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name='Email')
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nome} - {self.cpf})"


class Raca(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    especie = models.ForeignKey('Especie', on_delete=models.CASCADE, related_name='racas', null=True, blank=True)

    def __str__(self):
        return self.nome


class Animal(models.Model):
    PORTE_CHOICES = [
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Gigante'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='animais', verbose_name='Cliente')
    nome = models.CharField(max_length=100, verbose_name='Nome')
    raca = models.ForeignKey(Raca, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Raça')
    especie = models.ForeignKey('Especie', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Espécie')
    data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    porte = models.CharField(max_length=2, choices=PORTE_CHOICES, verbose_name='Porte')
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome})"
    
class Especie(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.descricao[:50]}..." if self.descricao else self.nome

class Veterinario(models.Model):
    nome = models.CharField(max_length=100)
    crmv = models.CharField(max_length=20, unique=True)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='O CPF deve conter exatamente 11 números.'
            )
        ]
    )
    especialidade = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.crmv})"


class Funcionario(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    cargo = models.CharField(max_length=50)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    data_contratacao = models.DateField()
    ativo = models.BooleanField(default=True)

    
    def __str__(self):
        return f"{self.nome} - {self.cargo}"




class ProdutoServico(models.Model):
    TIPO_CHOICES = (
        ('produto', 'Produto'),
        ('servico', 'Serviço'),
        ('vacina', 'Vacina'),
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    estoque = models.PositiveIntegerField(default=0)
    controlado = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    @property
    def tipo_legivel(self):
        return f"{self.nome} ({self.get_tipo_display()})"

    def __str__(self):
        # Se quiser só o nome:
        # return self.nome
        # Se quiser "Nome (Vacina/Serviço/Produto)":
        return self.tipo_legivel


class Agendamento(models.Model):
    TIPO_CHOICES = (
        ('consulta', 'Consulta'),
        ('exame', 'Exame'),
        ('cirurgia', 'Cirurgia'),
    )

    STATUS_CHOICES = (
        ('agendado', 'Agendado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    )

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Animal")
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, verbose_name="Veterinário")
    data_hora = models.DateTimeField(verbose_name="Data e Hora")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Atendimento")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendado', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.tipo.title()} - {self.animal.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class Venda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descricao = models.TextField(blank=True)
    data = models.DateTimeField(auto_now_add=True)
    # outros campos...

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(ProdutoServico, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario


class Cadastro_produto(models.Model):
    produto = models.ForeignKey(ProdutoServico, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade} unidades"


       

class AtendimentoClinico(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True)
    agendamento = models.ForeignKey(Agendamento, on_delete=models.SET_NULL, null=True, blank=True)
    data_hora = models.DateTimeField(default=timezone.now)
    anamnese = models.TextField(blank=True, null=True)
    sintomas = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    tratamento = models.TextField(blank=True, null=True)
    exames_solicitados = models.TextField(blank=True, null=True)
    orientacoes_ao_tutor = models.TextField(blank=True, null=True)
    retorno_recomendado = models.BooleanField(default=False)
    data_retorno = models.DateField(blank=True, null=True)
    venda_gerada = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')} ({self.veterinario})"
    


class VacinaAplicada(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vacinas_aplicadas')
    vacina = models.ForeignKey(ProdutoServico, on_delete=models.PROTECT, limit_choices_to={'tipo': 'vacina'})
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True)
    data_aplicacao = models.DateTimeField(default=timezone.now)
    dosagem = models.CharField(max_length=50, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    atendimento = models.ForeignKey('AtendimentoClinico', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.vacina.nome} em {self.animal.nome} ({self.data_aplicacao.strftime('%d/%m/%Y')})"