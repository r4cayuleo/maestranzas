import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Material, Location, StorageCapacity, Alert
from .forms import MaterialForm, LocationForm, UserRegisterForm, SearchForm, LocationSelectForm
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.forms import UserChangeForm


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('profile')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'inventory/profile.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.has_perm('inventory.can_manage_storage'):
        return redirect('responsable_almacen')
    elif request.user.has_perm('inventory.can_analyze_inventory'):
        return redirect('analista_inventario')
    elif request.user.has_perm('inventory.can_access_gerente'):
        return redirect('gerente')
    elif request.user.has_perm('inventory.can_access_gerente_inventario'):
        return redirect('gerente_inventario')
    elif request.user.has_perm('inventory.can_access_almacenero'):
        return redirect('almacenero')
    else:
        return render(request, 'inventory/no_permission.html')


@login_required
@permission_required('inventory.can_access_responsable_almacen', raise_exception=True)
def responsable_almacen_view(request):
    search_form = SearchForm(request.GET or None)
    location_select_form = LocationSelectForm(request.POST or None)
    materials = Material.objects.all()
    locations = Location.objects.all()
    capacity = StorageCapacity.objects.first()
    capacity_limit = capacity.limit if capacity else 1000
    total_quantity = materials.aggregate(Sum('quantity'))['quantity__sum'] or 0
    location_form = None
    alerts = Alert.objects.all()

    for location in locations:
        location.total_quantity = materials.filter(location=location).aggregate(Sum('quantity'))['quantity__sum'] or 0

    if request.method == "POST":
        if 'select_location' in request.POST:
            if location_select_form.is_valid():
                location = location_select_form.cleaned_data['location']
                location_form = LocationForm(instance=location)
        elif 'update_capacity' in request.POST:
            location_id = request.POST.get('location_id')
            location = get_object_or_404(Location, id=location_id)
            location_form = LocationForm(request.POST, instance=location)
            if location_form.is_valid():
                location_form.save()
                messages.success(request, 'Capacidad de ubicación actualizada.')
                return redirect('responsable_almacen')
        elif 'send_alert' in request.POST:
            alert_location_id = request.POST.get('alert_location_id')
            alert_location = get_object_or_404(Location, id=alert_location_id)
            alert = Alert(location=alert_location, created_by=request.user)
            alert.save()
            messages.success(request, 'Alerta establecida.')
        elif 'clear_alert' in request.POST:
            alert_id = request.POST.get('alert_id')
            alert = get_object_or_404(Alert, id=alert_id)
            alert.delete()
            messages.success(request, 'Alerta eliminada.')

    if request.GET:
        if search_form.is_valid():
            if search_form.cleaned_data['location']:
                materials = materials.filter(location=search_form.cleaned_data['location'])
            if search_form.cleaned_data['name']:
                materials = materials.filter(name__icontains=search_form.cleaned_data['name'])

    context = {
        'materials': materials,
        'search_form': search_form,
        'location_select_form': location_select_form,
        'location_form': location_form,
        'locations': locations,
        'total_quantity': total_quantity,
        'capacity_limit': capacity_limit,
        'alerts': alerts,
    }

    if total_quantity >= capacity_limit:
        context['capacity_alert'] = "Alerta: Capacidad máxima alcanzada"

    return render(request, 'inventory/responsable_almacen.html', context)


@login_required
@permission_required('inventory.can_access_almacenero', raise_exception=True)
def almacenero_view(request):
    materials = Material.objects.all()
    locations = Location.objects.all()
    capacity = StorageCapacity.objects.first()
    capacity_limit = capacity.limit if capacity else 1000
    total_quantity = materials.aggregate(Sum('quantity'))['quantity__sum'] or 0
    alerts = Alert.objects.all()

    if request.method == "POST":
        if 'clear_alert' in request.POST:
            alert_id = request.POST.get('alert_id')
            alert = get_object_or_404(Alert, id=alert_id)
            alert.delete()
            messages.success(request, 'Alerta eliminada.')
            return redirect('almacenero')

        if 'add_material' in request.POST:
            material_form = MaterialForm(request.POST)
            if material_form.is_valid():
                material = material_form.save(commit=False)
                material.added_by = request.user
                material.save()
                messages.success(request, 'Material registrado.')
                return redirect('almacenero')
        elif 'edit_material' in request.POST:
            material_id = request.POST.get('material_id')
            material_instance = get_object_or_404(Material, id=material_id)
            material_form = MaterialForm(request.POST, instance=material_instance)
            if material_form.is_valid():
                material_form.save()
                messages.success(request, 'Material actualizado.')
                return redirect('almacenero')
        elif 'delete_material' in request.POST:
            material_id = request.POST.get('material_id')
            material_instance = get_object_or_404(Material, id=material_id)
            material_instance.delete()
            messages.success(request, 'Material eliminado.')
            return redirect('almacenero')
    else:
        material_form = MaterialForm()
        if 'edit_material' in request.GET:
            material_id = request.GET.get('material_id')
            material_instance = get_object_or_404(Material, id=material_id)
            material_form = MaterialForm(instance=material_instance)

    context = {
        'material_form': material_form,
        'materials': materials,
        'locations': locations,
        'alerts': alerts,
        'total_quantity': total_quantity,
        'capacity_limit': capacity_limit,
    }

    if total_quantity >= capacity_limit:
        context['capacity_alert'] = "Alerta: Capacidad máxima alcanzada"

    return render(request, 'inventory/almacenero.html', context)


@login_required
@permission_required('inventory.can_access_analista_inventario', raise_exception=True)
def analista_inventario_view(request):
    materials = Material.objects.all()
    categories = materials.values('name').distinct()
    total_quantity = materials.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Formularios de búsqueda y selección
    search_form = SearchForm(request.GET or None)
    category_form = LocationSelectForm(request.POST or None)

    selected_materials = materials
    if request.GET:
        if search_form.is_valid():
            if search_form.cleaned_data['location']:
                selected_materials = selected_materials.filter(location=search_form.cleaned_data['location'])
            if search_form.cleaned_data['name']:
                selected_materials = selected_materials.filter(name__icontains=search_form.cleaned_data['name'])

    if request.method == "POST":
        if 'download_report' in request.POST:
            report_type = request.POST.get('report_type')
            return download_report(selected_materials, report_type)

    context = {
        'materials': materials,
        'total_quantity': total_quantity,
        'categories': categories,
        'search_form': search_form,
        'category_form': category_form,
        'selected_materials': selected_materials,
    }

    return render(request, 'inventory/analista_inventario.html', context)


@login_required
@permission_required('inventory.can_access_gerente_inventario', raise_exception=True)
def gerente_inventario_view(request):
    materials = Material.objects.all()
    locations = Location.objects.all()
    search_form = SearchForm(request.GET or None)
    location_form = LocationForm(request.POST or None)
    report = None
    search_results = None

    if request.method == "POST":
        if 'add_location' in request.POST:
            if location_form.is_valid():
                location_form.save()
                messages.success(request, 'Ubicación agregada.')
                return redirect('gerente_inventario')
        elif 'edit_location' in request.POST:
            location_id = request.POST.get('location_id')
            location_instance = get_object_or_404(Location, id=location_id)
            location_form = LocationForm(request.POST, instance=location_instance)
            if location_form.is_valid():
                location_form.save()
                messages.success(request, 'Ubicación actualizada.')
                return redirect('gerente_inventario')
        elif 'delete_location' in request.POST:
            location_id = request.POST.get('location_id')
            location_instance = get_object_or_404(Location, id=location_id)
            location_instance.delete()
            messages.success(request, 'Ubicación eliminada.')
            return redirect('gerente_inventario')
        elif 'generate_report' in request.POST:
            report = generate_report(request.POST.get('report_type'))

    if request.GET and search_form.is_valid():
        name = search_form.cleaned_data['name']
        location = search_form.cleaned_data['location']
        if name or location:
            filters = {}
            if name:
                filters['name__icontains'] = name
            if location:
                filters['location'] = location
            search_results = materials.filter(**filters)

    for location in locations:
        location.total_quantity = materials.filter(location=location).aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'search_form': search_form,
        'location_form': location_form,
        'materials': materials,
        'locations': locations,
        'report': report,
        'search_results': search_results,
    }
    return render(request, 'inventory/gerente_inventario.html', context)


@login_required
@permission_required('inventory.can_access_gerente', raise_exception=True)
def gerente_view(request):
    materials = Material.objects.all()
    locations = Location.objects.all()
    search_form = SearchForm(request.GET or None)
    report = None

    if request.method == "POST":
        report_type = request.POST.get('report_type')
        report = generate_report(report_type)

    for location in locations:
        location.total_quantity = materials.filter(location=location).aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'search_form': search_form,
        'materials': materials,
        'locations': locations,
        'report': report,
    }
    return render(request, 'inventory/gerente.html', context)


@login_required
@permission_required('inventory.can_access_gerente', raise_exception=True)
def generate_report_view(request):
    report_type = request.POST.get('report_type')
    report = generate_report(report_type)
    context = {'report': report}
    return render(request, 'inventory/generate_report.html', context)


def generate_report(report_type):
    if report_type == 'category':
        report = Material.objects.values('name').annotate(total_quantity=Sum('quantity'))
    elif report_type == 'inventory_status':
        report = Material.objects.all()
    elif report_type == 'historical':
        report = Material.objects.all()
    elif report_type == 'specific':
        report = Material.objects.all()
    elif report_type == 'movements':
        report = Material.objects.all()
    else:
        report = Material.objects.all()
    return report


def download_report(materials, report_type):
    if report_type == 'historical':
        filename = 'historical_report.csv'
        header = ['Nombre', 'Descripción', 'Cantidad', 'Ubicación', 'Registrado por', 'Fecha de Registro']
    elif report_type == 'category':
        filename = 'category_report.csv'
        header = ['Nombre', 'Descripción', 'Cantidad', 'Ubicación', 'Registrado por']
    elif report_type == 'specific':
        filename = 'specific_report.csv'
        header = ['Nombre', 'Descripción', 'Cantidad', 'Ubicación', 'Registrado por']
    elif report_type == 'movements':
        filename = 'movements_report.csv'
        header = ['Nombre', 'Descripción', 'Cantidad', 'Ubicación', 'Fecha de Movimiento']
    else:
        filename = 'inventory_report.csv'
        header = ['Nombre', 'Descripción', 'Cantidad', 'Ubicación', 'Registrado por']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(header)

    for material in materials:
        row = [material.name, material.description, material.quantity, material.location.name, material.added_by.username, material.date_added] if report_type in ['historical', 'movements'] else [material.name, material.description, material.quantity, material.location.name, material.added_by.username]
        writer.writerow(row)

    return response


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})
