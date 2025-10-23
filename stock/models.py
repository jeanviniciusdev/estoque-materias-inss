from django.db import models
from django.conf import settings
from django.db import transaction

class Material(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='materiais/', null=True, blank=True)
    quantidade = models.IntegerField(default=0)
    minimo = models.IntegerField(default=0)
    criado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"

class Movimento(models.Model):
    MATERIAL_TIPOS = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('ADICAO', 'Adição (inicial)'),
        ('DELETE', 'Delete'),
    ]
    # permitir null e usar SET_NULL para preservar movimentos após exclusão do material
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name='movimentos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=10, choices=MATERIAL_TIPOS)
    quantidade = models.IntegerField()
    nota = models.CharField(max_length=200, blank=True)
    criado = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Ao salvar:
         - se criação: aplica efeito no material (salva material) exceto para DELETE;
         - se atualização: reverte efeito do registro anterior e aplica o novo (cuida de mudança de material/tipo/quantidade);
        Use kwargs.pop('adjust_material', True) para evitar ajuste automático em casos especiais.
        """
        adjust = kwargs.pop('adjust_material', True)
        positive = ('ENTRADA', 'ADICAO')
        negative = ('SAIDA',)

        with transaction.atomic():
            if self.pk:
                # atualização: reverte o efeito anterior e aplica o novo
                prev = Movimento.objects.select_for_update().get(pk=self.pk)
                if adjust:
                    # reverter efeito anterior no material antigo (se existir)
                    if prev.material:
                        if prev.tipo in positive:
                            prev.material.quantidade -= prev.quantidade
                        elif prev.tipo in negative:
                            prev.material.quantidade += prev.quantidade
                        # prev.tipo == 'DELETE' não altera quantidade
                        prev.material.save()
                    # aplicar efeito novo no material atual (se existir)
                    if self.material:
                        if self.tipo in positive:
                            self.material.quantidade += self.quantidade
                        elif self.tipo in negative:
                            self.material.quantidade -= self.quantidade
                        # tipo == 'DELETE' não altera quantidade
                        self.material.save()
            else:
                # criação: aplica efeito normalmente (se existir material)
                if adjust and self.material:
                    if self.tipo in positive:
                        self.material.quantidade += self.quantidade
                    elif self.tipo in negative:
                        self.material.quantidade -= self.quantidade
                    # DELETE não altera quantidade
                    self.material.save()

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Ao remover um movimento, reverte seu efeito sobre o material (opcional via adjust_material).
        """
        adjust = kwargs.pop('adjust_material', True)
        positive = ('ENTRADA', 'ADICAO')
        negative = ('SAIDA',)

        with transaction.atomic():
            if adjust and self.material:
                if self.tipo in positive:
                    self.material.quantidade -= self.quantidade
                elif self.tipo in negative:
                    self.material.quantidade += self.quantidade
                # DELETE não altera quantidade
                self.material.save()
            super().delete(*args, **kwargs)
