
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from .models import Material
from .forms import MaterialForm, MovimentoForm
from .serializers import MaterialSerializer
from rest_framework.decorators import api_view
from django.http import HttpResponse
import csv
from django.utils.dateparse import parse_datetime, parse_date
from .models import Movimento
from io import BytesIO

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

@login_required
def dashboard(request):
    materiais = Material.objects.all()
    return render(request, 'stock/dashboard.html', {'materiais': materiais})

@login_required
def material_list(request):
    materiais = Material.objects.all()
    return render(request, 'stock/materials_list.html', {'materiais': materiais})

@login_required
def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            mat = form.save()
            # registrar movimento inicial quando houver quantidade
            if mat.quantidade and mat.quantidade > 0:
                # Não ajustar a quantidade do material aqui porque já foi salva no material
                mv = Movimento(material=mat, tipo='ADICAO', quantidade=mat.quantidade)
                if request.user.is_authenticated:
                    mv.usuario = request.user
                # salvar sem ajustar a quantidade do material (adjust_material=False)
                mv.save(adjust_material=False)
            return redirect('materials_list')
    else:
        form = MaterialForm()
    return render(request, 'stock/material_form.html', {'form': form})

@login_required  
def material_edit(request, pk):
    mat = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=mat)
        if form.is_valid():
            form.save()
            return redirect('materials_list')
    else:
        form = MaterialForm(instance=mat)
    return render(request, 'stock/material_form.html', {'form': form})

# Apenas staff pode deletar
@login_required
@user_passes_test(lambda u: u.is_staff)
def material_delete(request, pk):
    mat = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        mat.delete()
        return redirect('materials_list')
    return render(request, 'stock/material_confirm_delete.html', {'material': mat})

@login_required
def movimento_create(request):
    if request.method == 'POST':
        form = MovimentoForm(request.POST)
        if form.is_valid():
            mv = form.save(commit=False)
            if request.user.is_authenticated:
                mv.usuario = request.user
            mv.save()
            return redirect('materials_list')
    else:
        form = MovimentoForm()
    return render(request, 'stock/movimento_form.html', {'form': form})

@api_view(['GET'])
def api_materials(request):
    materiais = Material.objects.all().order_by('nome')
    data = [
        {
            'id': m.id,
            'nome': m.nome,
            'quantidade': m.quantidade,
            'minimo': m.minimo  # ✅ incluído para o gráfico 2
        }
        for m in materiais
    ]
    return JsonResponse(data, safe=False)


@login_required
def export_materials_csv(request):
    materiais = Material.objects.all().order_by('nome')
    # Content-Type CSV (UTF-8)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="materiais.csv"'
    # BOM para compatibilidade com Excel (Windows)
    response.write('\ufeff')
    # garantir CRLF (Windows) como terminador de linha
    writer = csv.writer(response, lineterminator='\r\n')
    writer.writerow(['ID', 'Nome', 'Descrição', 'Quantidade', 'Mínimo'])
    for m in materiais:
        writer.writerow([m.id, m.nome, m.descricao, m.quantidade, m.minimo])
    return response


    

@login_required
def export_movements_csv(request):
    """Exporta movimentos (transações) em CSV. Aceita filtros via querystring: "start" e "end" (YYYY-MM-DD).
    Colunas: id,material_id,material_nome,tipo,quantidade,nota,criado"""
    qs = Movimento.objects.select_related('material').all().order_by('-criado')
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        try:
            sd = parse_date(start)
            if sd:
                qs = qs.filter(criado__date__gte=sd)
        except Exception:
            pass
    if end:
        try:
            ed = parse_date(end)
            if ed:
                qs = qs.filter(criado__date__lte=ed)
        except Exception:
            pass

    # Content-Type CSV (UTF-8)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="movimentos.csv"'
    # BOM para compatibilidade com Excel (Windows)
    response.write('\ufeff')
    # garantir CRLF (Windows) como terminador de linha
    writer = csv.writer(response, lineterminator='\r\n')
    writer.writerow(['id', 'data', 'usuario', 'material_id', 'material_nome', 'tipo', 'quantidade', 'nota'])
    for mv in qs:
        usuario = mv.usuario.username if getattr(mv, 'usuario', None) else ''
        data_str = mv.criado.strftime('%d/%m/%Y') if getattr(mv, 'criado', None) else ''
        writer.writerow([mv.id, data_str, usuario, mv.material.id, mv.material.nome, mv.tipo, mv.quantidade, mv.nota])
    return response
