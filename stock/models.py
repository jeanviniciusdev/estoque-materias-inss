
from django.db import models
from django.conf import settings

class Material(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    quantidade = models.IntegerField(default=0)
    minimo = models.IntegerField(default=0)
    criado = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='materials_created'
    )

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"

class Movimento(models.Model):
    MATERIAL_TIPOS = [('ENTRADA', 'Entrada'), ('SAIDA', 'Saída'), ('ADICAO', 'Adição (inicial)')]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='movimentos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=10, choices=MATERIAL_TIPOS)
    quantidade = models.IntegerField()
    nota = models.CharField(max_length=200, blank=True)
    criado = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # atualiza a quantidade do material quando salva movimento
        # aceitar kwargs opcional 'adjust_material' para controlar se a quantidade do material deve ser atualizada
        adjust = kwargs.pop('adjust_material', True)
        novo = not bool(self.pk)
        if novo and adjust:
            if self.tipo in ('ENTRADA', 'ADICAO'):
                self.material.quantidade += self.quantidade
            else:
                self.material.quantidade -= self.quantidade
            self.material.save()
        super().save(*args, **kwargs)

        # --- NOTIFICAÇÃO: somente se ajustamos o material e agora ele está abaixo do mínimo ---
        # Apenas criar notificação se adjust=True e a quantidade atual estiver < minimo
        try:
            if adjust and self.material.quantidade < self.material.minimo:
                owner = self.material.created_by
                if owner:
                    existing = Notification.objects.filter(
                        user=owner,
                        material=self.material,
                        read=False,
                        message__contains='Abaixo do mínimo'
                    ).exists()
                    if not existing:
                        Notification.objects.create(
                            user=owner,
                            material=self.material,
                            message=f"O material '{self.material.nome}' ficou abaixo do mínimo ({self.material.quantidade}/{self.material.minimo})."
                        )
        except Exception as e:
            pass
#Novas funções

#Notifications
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    message = models.CharField(max_length=255, default='-')
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notif para {self.user}: {self.message[:40]}"