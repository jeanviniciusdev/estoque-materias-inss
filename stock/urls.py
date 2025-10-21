
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('materials/', views.material_list, name='materials_list'),
    path('materials/add/', views.material_create, name='materials_add'),
    path('materials/<int:pk>/edit/', views.material_edit, name='materials_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='materials_delete'),
    path('movimentos/add/', views.movimento_create, name='movimento_add'),
    path('api/materials/', views.api_materials, name='api_materials'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('reports/materials/csv/', views.export_materials_csv, name='export_materials_csv'),
    path('reports/movements/csv/', views.export_movements_csv, name='export_movements_csv'),
    path('alertas/', views.alertas_completos, name='alertas_completos'),
    path('export_alertas_csv/', views.export_alertas_csv, name='export_alertas_csv'),
]
