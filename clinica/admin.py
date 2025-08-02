from django.contrib import admin   
from clinica import models



# Register your models here.
@admin.register(models.Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome',  'cpf', 'cidade', 'data_criacao')
    search_fields = ('nome',  'cpf')
    list_filter = ('cidade',)   

@admin.register(models.Raca)
class RacaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)  
    list_filter = ('especie',)
    


@admin.register(models.Animal)
class CachorroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'raca', 'data_nascimento', 'porte')
    search_fields = ('nome', 'cliente__nome', 'raca__nome')
    list_filter = ('porte', 'raca') 


@admin.register(models.Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    list_filter = ('descricao',)        

@admin.register(models.Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'veterinario', 'data_hora', 'tipo', 'status')
    search_fields = ('animal__nome', 'veterinario__nome')
    list_filter = ('tipo', 'status', 'data_hora') 
    date_hierarchy = 'data_hora'

@admin.register(models.Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):   
    list_display = ('nome', 'especialidade', 'crmv')
    search_fields = ('nome', 'crmv')
    list_filter = ('especialidade',)

@admin.register(models.Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):   
    list_display = ('nome', 'cpf', 'cargo', 'data_contratacao', 'ativo')
    search_fields = ('nome', 'cpf', 'cargo')
    list_filter = ('cargo', 'ativo')

class AgendamentoInline(admin.TabularInline):
    model = models.Agendamento
    extra = 1   
    fields = ('animal', 'veterinario', 'data_hora', 'tipo', 'status', 'observacoes')        


@admin.register(models.ProdutoServico)
class ProdutoServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'tipo')
    search_fields = ('nome',)
    list_filter = ('tipo',)