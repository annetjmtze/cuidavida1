
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# 🔹 IMPORTAR MODELOS
from .models import Perfil, Paciente, Medico


# 🔹 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🔹 WIZARD (puedes luego conectarlo al paciente)
def wizard(request):

    if request.method == "POST":

        # datos del paso 1
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")

        # datos del paso 2
        usuario = request.POST.get("usuario")
        password = request.POST.get("password")

        print(nombre, correo, usuario)

        # aquí puedes guardar en la base de datos

        return redirect("dashboard")

    return render(request, "wizard.html")


# 🔹 REGISTRO (AQUÍ ESTÁ LO IMPORTANTE 🔥)
def registro(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        nombre = request.POST['nombre']
        tipo = request.POST['tipo']

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
                telefono=''
            )

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
            return redirect('dashboard')

        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'login.html')


# 🔹 DASHBOARD (REDIRECCIÓN SEGÚN TIPO 🔥)
@login_required
def dashboard(request):

    perfil = request.user.perfil  # obtiene si es paciente o médico
    print(dict(request.session))

    if perfil.tipo == 'medico':
        return render(request, 'prototipo_medico.html')
    else:
        return render(request, 'prototipo.html')
