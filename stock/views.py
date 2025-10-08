
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from .models import Material
from .forms import MaterialForm, MovimentoForm
from .serializers import MaterialSerializer
from rest_framework.decorators import api_view

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
            form.save()
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
            form.save()
            return redirect('materials_list')
    else:
        form = MovimentoForm()
    return render(request, 'stock/movimento_form.html', {'form': form})

@api_view(['GET'])
def api_materials(request):
    qs = Material.objects.all()
    serializer = MaterialSerializer(qs, many=True)
    return JsonResponse(serializer.data, safe=False)
