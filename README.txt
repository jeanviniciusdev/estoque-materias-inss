
Projeto: Gestão Materiais INSS
-----------------------------

Este pacote contém um projeto Django pronto para rodar localmente usando SQLite.

Como rodar (passo a passo para iniciantes):
1. Extraia o zip em uma pasta (por exemplo C:\Users\SeuNome\Documents\gestao_materiais_inss ou ~/gestao_materiais_inss).
2. Abra o terminal e navegue até a pasta do projeto (a pasta que contém manage.py).
3. (Recomendado) Crie e ative um ambiente virtual:
   Windows (PowerShell):
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
   macOS / Linux:
     python3 -m venv .venv
     source .venv/bin/activate
4. Instale dependências:
   pip install -r requirements.txt
5. Rode migrações (cria o banco SQLite):
   python manage.py migrate
6. Crie um superuser (conta admin):
   python manage.py createsuperuser
7. Rode o servidor de desenvolvimento:
   python manage.py runserver
8. Abra no navegador: http://127.0.0.1:8000/  (Dashboard)
   Admin: http://127.0.0.1:8000/admin/

Observações:
- Usuários normais podem ser criados no admin (não marcar 'Staff status').
- Apenas usuários com 'Staff' podem excluir materiais.
- O gráfico utiliza Chart.js e mostra as quantidades atuais por material.
