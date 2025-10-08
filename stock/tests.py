
from django.test import TestCase
from .models import Material, Movimento

class MaterialMovimentoTests(TestCase):
    def test_entrada_atualiza_quantidade(self):
        m = Material.objects.create(nome='Caneta', quantidade=10)
        Movimento.objects.create(material=m, tipo='ENTRADA', quantidade=5)
        m.refresh_from_db()
        self.assertEqual(m.quantidade, 15)

    def test_saida_atualiza_quantidade(self):
        m = Material.objects.create(nome='Papel', quantidade=20)
        Movimento.objects.create(material=m, tipo='SAIDA', quantidade=7)
        m.refresh_from_db()
        self.assertEqual(m.quantidade, 13)
