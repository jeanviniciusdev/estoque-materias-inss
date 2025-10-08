
from django.contrib import admin
from .models import Material, Movimento

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'minimo')

@admin.register(Movimento)
class MovimentoAdmin(admin.ModelAdmin):
    list_display = ('material', 'tipo', 'quantidade', 'criado')
