
from django.contrib import admin
from .models import Material, Movimento

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'minimo', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.imagem:
            return f"<img src='{obj.imagem.url}' style='max-height:60px; max-width:120px; object-fit:cover;'/>"
        return ''
    preview.allow_tags = True
    preview.short_description = 'Imagem'

@admin.register(Movimento)
class MovimentoAdmin(admin.ModelAdmin):
    list_display = ('material', 'tipo', 'quantidade', 'criado')
