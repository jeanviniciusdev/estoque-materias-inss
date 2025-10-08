
from django.db import models

class Material(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    quantidade = models.IntegerField(default=0)
    minimo = models.IntegerField(default=0)
    criado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"

class Movimento(models.Model):
    MATERIAL_TIPOS = [('ENTRADA', 'Entrada'), ('SAIDA', 'Saída')]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='movimentos')
    tipo = models.CharField(max_length=10, choices=MATERIAL_TIPOS)
    quantidade = models.IntegerField()
    nota = models.CharField(max_length=200, blank=True)
    criado = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # atualiza a quantidade do material quando salva movimento
        novo = not bool(self.pk)
        if novo:
            if self.tipo == 'ENTRADA':
                self.material.quantidade += self.quantidade
            else:
                self.material.quantidade -= self.quantidade
            self.material.save()
        super().save(*args, **kwargs)
