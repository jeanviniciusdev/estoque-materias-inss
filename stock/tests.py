
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
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

    def test_export_materials_csv(self):
        Material.objects.create(nome='Caneta', quantidade=10)
        # acessar via reverse e com login
        User = get_user_model()
        u = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(u)
        url = reverse('export_materials_csv')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200,))
        self.assertTrue(resp['Content-Type'].startswith('text/csv'))
    
    def test_export_movements_csv(self):
        User = get_user_model()
        u = User.objects.create_user(username='tester2', password='pass')
        self.client.force_login(u)
        url = reverse('export_movements_csv')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200,))
        self.assertTrue(resp['Content-Type'].startswith('text/csv'))

    def test_material_creation_registers_adicao_movement(self):
        User = get_user_model()
        u = User.objects.create_user(username='creator', password='pass')
        self.client.force_login(u)
        # criar material via view
        resp = self.client.post(reverse('materials_add'), {'nome': 'Lapis', 'quantidade': 12, 'minimo': 1})
        self.assertIn(resp.status_code, (302,))
        m = Material.objects.get(nome='Lapis')
        # deve existir um movimento do tipo ADICAO
        movs = m.movimentos.filter(tipo='ADICAO')
        self.assertTrue(movs.exists())
        mv = movs.first()
        self.assertEqual(mv.quantidade, 12)