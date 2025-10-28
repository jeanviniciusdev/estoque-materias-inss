from django.core.management.base import BaseCommand
from django.db import transaction

from stock.models import Movimento


class Command(BaseCommand):
    help = (
        "Remove todos os registros de Movimento sem alterar as quantidades de Material.\n"
        "Use --fast para usar deleção em massa (mais rápida)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirma a operação sem perguntar",
        )
        parser.add_argument(
            "--fast",
            action="store_true",
            help="Usa QuerySet.delete() (rápido, ignora delete() customizado)",
        )

    def handle(self, *args, **options):
        confirm = options.get("yes", False)
        fast = options.get("fast", False)

        total = Movimento.objects.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nenhum movimento para remover."))
            return

        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    f"Isto irá remover {total} movimentos e NÃO alterará as quantidades dos materiais."
                )
            )
            resp = input("Digite 'SIM' para confirmar: ")
            if resp.strip().upper() != "SIM":
                self.stdout.write(self.style.ERROR("Operação cancelada."))
                return

        if fast:
            # Deleção em massa: não chama Model.delete(), portanto não ajusta materiais
            deleted, _ = Movimento.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Movimentos removidos (método rápido): {deleted}"))
            return

        # Caminho seguro: itera e garante adjust_material=False por instância
        removed = 0
        with transaction.atomic():
            for mv in Movimento.objects.iterator(chunk_size=1000):
                mv.delete(adjust_material=False)
                removed += 1
        self.stdout.write(self.style.SUCCESS(f"Movimentos removidos: {removed}"))

