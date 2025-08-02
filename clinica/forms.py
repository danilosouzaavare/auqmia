from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import render

from django import forms
from django.forms import inlineformset_factory
from .models import AtendimentoClinico, VacinaAplicada


from . import models

class ClienteForm(forms.ModelForm):
    class Meta:
        model = models.Cliente
        fields = ['nome',  'cpf', 'endereco', 'cidade', 'cep', 'telefone', 'telefone_2', 'email']
        

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf or len(cpf) != 11:
            raise ValidationError("CPF deve ter 11 caracteres.")
        return cpf
    
class RacaForm(forms.ModelForm):
    class Meta:
        model = models.Raca
        fields = ['nome', 'especie']

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise ValidationError("O nome da raça é obrigatório.")
        return nome     


class AnimalForm(forms.ModelForm):
    class Meta:
        model = models.Animal
        fields = ['cliente', 'nome', 'especie', 'raca', 'data_nascimento', 'porte', 'observacoes']

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise ValidationError("O nome do animal é obrigatório.")
        return nome

class EspecieForm(forms.ModelForm):
    class Meta:
        model = models.Especie
        fields = ['nome', 'descricao']

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise ValidationError("O nome da espécie é obrigatório.")
        return nome
    
class UserRegistrationForm(UserCreationForm):   
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("O email é obrigatório.")
        return email
    


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = models.Agendamento
        fields = ['animal', 'veterinario', 'data_hora', 'tipo', 'status', 'observacoes']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class ProdutoServicoForm(forms.ModelForm):
    class Meta:
        model = models.ProdutoServico
        fields = ['nome', 'descricao', 'preco', 'tipo']
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise ValidationError("O nome do produto ou serviço é obrigatório.")
        return nome.strip()
    




class AtendimentoClinicoForm(forms.ModelForm):
    class Meta:
        model = AtendimentoClinico
        fields = '__all__'
        widgets = {
            'data_retorno': forms.DateInput(attrs={'type': 'date'}),
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

VacinaAplicadaFormSet = inlineformset_factory(
    AtendimentoClinico,
    VacinaAplicada,
    fields=['vacina', 'dosagem', 'observacoes'],
    extra=1,
    can_delete=True
)