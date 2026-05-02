from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
#DEBEMOS CREAR UNA VISTA EN DJANGO QUE RECIBA UN CP, Y LO CONVIERTA A INFORMACIÓ GEOGRÁFUCA EN JSON
# 🔹 IMPORTAR MODELOS
from .models import Perfil, Paciente, Medico, CodigoPostal


# 🔹 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🔹 WIZARD (puedes luego conectarlo al paciente)
@login_required
def wizard(request):
    if request.method == "POST":
        try:
            # Obtenemos el perfil del paciente del usuario actual
            paciente = request.user.paciente
            
            # Asignamos los datos del formulario al objeto paciente
            paciente.nombre = request.POST.get("nombre")
            paciente.edad = request.POST.get("edad")
            paciente.curp = request.POST.get("curp")
            paciente.fecha_nacimiento = request.POST.get("fecha_nacimiento")
            paciente.sexo = request.POST.get("sexo")
            paciente.tipo_sangre = request.POST.get("tipo_sangre")
            
            # Para las enfermedades (checkboxes), usamos getlist
            enfermedades = request.POST.getlist("enfermedades")
            paciente.enfermedades = ", ".join(enfermedades)
            
            paciente.antecedentes = request.POST.get("antecedentes")
            paciente.medicamentos = request.POST.get("medicamentos")
            paciente.telefono = request.POST.get("telefono")
            paciente.cp = request.POST.get("cp")
            paciente.estado = request.POST.get("estado")
            paciente.municipio = request.POST.get("municipio")
            paciente.colonia = request.POST.get("colonia")
            paciente.direccion = request.POST.get("direccion")
            paciente.hospital = request.POST.get("hospital")
            paciente.num_seguro = request.POST.get("seguro")
            
            # Guardamos los cambios en la base de datos
            paciente.save()
            
        except Exception as e:
            print(f"Error al guardar el wizard: {e}")
            
        return redirect("dashboard")

    return render(request, "wizard.html")


# 🔹 REGISTRO (AQUÍ ESTÁ LO IMPORTANTE 🔥)
def registro(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        nombre = request.POST['nombre']
        tipo = request.POST['tipo']
        cedula = request.POST.get('cedula', '')

        try:
            with transaction.atomic():
                # Crear usuario
                user = User.objects.create_user(username=username, password=password)

                # Crear perfil
                perfil = Perfil.objects.create(user=user, tipo=tipo)

                # Crear paciente o médico según tipo
                if tipo == 'paciente':
                    Paciente.objects.create(
                        user=user,
                        nombre=nombre,
                        edad=0,
                        telefono='',
                        direccion=''
                    )
                else:
                    Medico.objects.create(
                        user=user,
                        nombre=nombre,
                        especialidad='',
                        telefono='',
                        direccion='',
                        cedula=cedula
                    )
        except Exception as e:
            # Si algo falla (ej. cédula inválida), volvemos a mostrar el registro con el error
            return render(request, 'registro.html', {'error': 'Hubo un error al registrar: ' + str(e)})

        return redirect('login')

    return render(request, 'registro.html')


# 🔹 LOGIN
def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # VALIDACIÓN DE DATOS EN BACKEND
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'login.html')


# 🔹 DASHBOARD (REDIRECCIÓN SEGÚN TIPO 🔥)
@login_required
def dashboard(request):
    try:
        # Intentamos obtener el perfil
        perfil = request.user.perfil 
    except Exception:
        # Si el usuario no tiene perfil (ej. es un Superusuario de la terminal)
        if request.user.is_superuser:
            return redirect('/admin/')
        # Si es un usuario normal sin perfil, lo sacamos para evitar errores
        logout(request)
        return redirect('login')

    if perfil.tipo == 'medico':
        return render(request, 'prototipo_medico.html')
    else:
        # Obtenemos el objeto paciente para pasar sus datos al HTML
        paciente = getattr(request.user, 'paciente', None)
        context = {
            'paciente': paciente,
            'edad': paciente.edad if paciente else "N/A",
            'tipo_sangre': paciente.tipo_sangre if paciente else "N/A",
        }
        return render(request, 'prototipo.html', context)
#MUCHAS DUDAS AQUÍ-----------------------------------------------
# 🔹 API PARA VALIDAR CÓDIGO POSTAL
def buscar_cp(request):
    cp = request.GET.get('cp')
    cp = request.GET.get('cp', '').strip()
    
    # Esto aparecerá en tu terminal donde corres el server
    print(f"--- Buscando CP: {cp} ---")
    
    resultados = CodigoPostal.objects.filter(codigo=cp)
    
    if resultados.exists():
        data = {
            'estado': resultados[0].estado,
            'municipio': resultados[0].municipio,
            'colonias': [r.asentamiento for r in resultados]
        }
        return JsonResponse({'success': True, 'data': data})
    
    return JsonResponse({'success': False, 'error': 'Código postal no encontrado'})
