from django.db import models
from django.conf import settings
from django.db import transaction

class Material(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    quantidade = models.IntegerField(default=0)
    minimo = models.IntegerField(default=0)
    criado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"

class Movimento(models.Model):
    MATERIAL_TIPOS = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('ADICAO', 'Adição'),
        ('DELETE', 'Delete'),
        ('EMPRESTIMO', 'Empréstimo'),
    ]
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name='movimentos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=12, choices=MATERIAL_TIPOS)
    quantidade = models.IntegerField()
    nota = models.CharField(max_length=200, blank=True)
    data_devolucao = models.DateField(null=True, blank=True)
    criado = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # ajustar comportamento de alteração de quantidade via kwargs
        adjust = kwargs.pop('adjust_material', True)
        positive = ('ENTRADA', 'ADICAO')
        negative = ('SAIDA',)  # EMPRESTIMO não altera quantidade
        with transaction.atomic():
            if self.pk:
                prev = Movimento.objects.select_for_update().get(pk=self.pk)
                if adjust:
                    # reverter efeito do movimento anterior (se houver material)
                    if prev.material:
                        if prev.tipo in positive:
                            prev.material.quantidade -= prev.quantidade
                        elif prev.tipo in negative:
                            prev.material.quantidade += prev.quantidade
                        prev.material.save()
                    # aplicar efeito do novo movimento (se houver material)
                    if self.material:
                        if self.tipo in positive:
                            self.material.quantidade += self.quantidade
                        elif self.tipo in negative:
                            self.material.quantidade -= self.quantidade
                        # EMPRESTIMO e DELETE não alteram quantidade
                        self.material.save()
            else:
                # criação: aplicar efeito quando aplicável
                if adjust and self.material:
                    if self.tipo in positive:
                        self.material.quantidade += self.quantidade
                    elif self.tipo in negative:
                        self.material.quantidade -= self.quantidade
                    # EMPRESTIMO e DELETE não alteram quantidade
                    self.material.save()

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        adjust = kwargs.pop('adjust_material', True)
        positive = ('ENTRADA', 'ADICAO')
        negative = ('SAIDA',)  # EMPRESTIMO não altera quantidade
        with transaction.atomic():
            if adjust and self.material:
                if self.tipo in positive:
                    self.material.quantidade -= self.quantidade
                elif self.tipo in negative:
                    self.material.quantidade += self.quantidade
                # EMPRESTIMO and DELETE: nada a reverter na quantidade
                self.material.save()
            super().delete(*args, **kwargs)

        @property
        def status_display(self):
            if self.tipo == 'DEVOLVIDO':
                return 'Devolvido'
            if self.tipo == 'EMPRESTIMO':
                if self.data_devolucao:
                    if self.data_devolucao < timezone.now().date():
                        return 'Atrasado'
                    else:
                        return 'Pendente'
                return 'Sem data'
            return '-'