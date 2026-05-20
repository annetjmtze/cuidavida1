import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse # Import HttpResponse for PDF serving
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Avg
# 🔹 IMPORTAR MODELOS

# For PDF generation
import io
from django.template.loader import get_template
from xhtml2pdf import pisa # Make sure to install xhtml2pdf: pip install xhtml2pdf
from .models import Perfil, Paciente, Medico, CodigoPostal, Receta, Cita, ContactoEmergencia, Valoracion, Alerta


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
            
            # Limpieza y asignación de datos
            edad_raw = request.POST.get("edad", "0")
            paciente.nombre = request.POST.get("nombre", "").strip()
            paciente.edad = int(edad_raw) if edad_raw.isdigit() else 0
            paciente.curp = request.POST.get("curp", "").strip().upper()
            paciente.fecha_nacimiento = request.POST.get("fecha_nacimiento") or None
            paciente.sexo = request.POST.get("sexo", "").strip()
            paciente.tipo_sangre = request.POST.get("tipo_sangre", "").strip()

            # Actualizar el correo en el modelo User si se proporciona
            nuevo_correo = request.POST.get("correo", "").strip()
            if nuevo_correo:
                request.user.email = nuevo_correo
                request.user.save()
            
            paciente.enfermedades = ", ".join(request.POST.getlist("enfermedades"))
            paciente.antecedentes = request.POST.get("antecedentes", "").strip()
            paciente.medicamentos = request.POST.get("medicamentos", "").strip()
            paciente.telefono = request.POST.get("telefono", "").strip()
            paciente.cp = request.POST.get("cp", paciente.cp).strip()
            paciente.estado = request.POST.get("estado", paciente.estado).strip()
            paciente.municipio = request.POST.get("municipio", paciente.municipio).strip()
            paciente.colonia = request.POST.get("colonia", paciente.colonia).strip()
            paciente.direccion = request.POST.get("direccion", "").strip()
            paciente.hospital = request.POST.get("hospital", "").strip()
            paciente.num_seguro = request.POST.get("seguro", "").strip()
            
            # Procesar foto si se subió una nueva
            if request.FILES.get("foto"):
                paciente.foto = request.FILES.get("foto")

            # Procesar contactos de emergencia
            # Para simplificar el prototipo, reemplazamos los contactos anteriores con los nuevos
            paciente.contactos_emergencia.all().delete()
            c_nombres = request.POST.getlist("cont_nombre")
            c_relaciones = request.POST.getlist("cont_relacion")
            c_telefonos = request.POST.getlist("cont_telefono")

            for n, r, t in zip(c_nombres, c_relaciones, c_telefonos):
                if n.strip() and t.strip():
                    ContactoEmergencia.objects.create(
                        paciente=paciente,
                        nombre=n.strip(),
                        relacion=r.strip(),
                        telefono=t.strip()
                    )

            # Vincular con el médico seleccionado si existe
            medico_id = request.POST.get("medico_asignado")
            if medico_id:
                paciente.medico_asignado_id = medico_id
            
            # Guardamos los cambios en la base de datos
            paciente.save()
            
        except Exception as e:
            print(f"Error al guardar el wizard: {e}")
            
        return redirect("dashboard")

    # Obtenemos contactos existentes para pre-cargar el formulario
    paciente = getattr(request.user, 'paciente', None)
    contactos = paciente.contactos_emergencia.all() if paciente else []
    # Pasamos la lista de todos los médicos registrados para que el paciente elija
    medicos = Medico.objects.all()
    return render(request, "wizard.html", {'medicos': medicos, 'contactos': contactos, 'paciente': paciente})


# 🔹 REGISTRO (AQUÍ ESTÁ LO IMPORTANTE 🔥)
def registro(request):

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        nombre = request.POST.get('nombre', '').strip()
        tipo = request.POST.get('tipo', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        foto = request.FILES.get('foto')

        try:
            with transaction.atomic():
                # Crear usuario
                user = User.objects.create_user(username=username, password=password, email=email)

                # Crear perfil
                perfil = Perfil.objects.create(user=user, tipo=tipo)

                # Crear paciente o médico según tipo
                if tipo == 'paciente':
                    Paciente.objects.create(
                        user=user,
                        nombre=nombre,
                        edad=0,
                        telefono='',
                        direccion='',
                        foto=foto
                    )
                else:
                    Medico.objects.create(
                        user=user,
                        nombre=nombre,
                        especialidad='',
                        telefono='',
                        direccion='',
                        cedula=cedula,
                        foto=foto
                    )
        except Exception as e:
            # Si algo falla (ej. cédula inválida), volvemos a mostrar el registro con el error
            return render(request, 'registro.html', {'error': 'Hubo un error al registrar: ' + str(e)})

        # 🔹 Enviar correo de confirmación (Trigger)
        if email:
            send_mail(
                subject='¡Bienvenido a CuidaVida!',
                message=f'Hola {nombre},\n\nTu cuenta como {tipo} ha sido creada exitosamente. Ya puedes acceder a la plataforma.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

        return redirect('login')

    return render(request, 'registro.html')


# 🔹 LOGIN
def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

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
        medico = request.user.medico
        pacientes = medico.pacientes.all()
        hoy = timezone.now().date()
        citas_hoy = medico.citas_medico.filter(fecha=hoy).order_by('hora')
        proximas_citas = medico.citas_medico.filter(fecha__gt=hoy).order_by('fecha', 'hora')
        recetas_emitidas = Receta.objects.filter(medico=medico).order_by('paciente__nombre', '-fecha')
        
        # Estadísticas dinámicas para el médico
        pendientes_hoy = citas_hoy.filter(estatus='pendiente').count()
        rating_promedio = Valoracion.objects.filter(medico=medico).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
        total_valoraciones = Valoracion.objects.filter(medico=medico).count()
        ultimas_valoraciones = Valoracion.objects.filter(medico=medico).order_by('-fecha')[:5]

        # Alertas críticas pendientes (no resueltas) para el médico
        critical_alerts = Alerta.objects.filter(medico=medico, resuelto=False).order_by('-timestamp')

        # Desglose de calificaciones para la pestaña de estadísticas
        rating_dist = []
        for i in range(5, 0, -1):
            count = Valoracion.objects.filter(medico=medico, puntuacion=i).count()
            percentage = (count / total_valoraciones * 100) if total_valoraciones > 0 else 0
            rating_dist.append({'stars': i, 'count': count, 'percentage': round(percentage, 1)})
        
        return render(request, 'prototipo_medico.html', {
            'pacientes': pacientes,
            'medico': medico,
            'citas_hoy': citas_hoy,
            'proximas_citas': proximas_citas,
            'recetas_emitidas': recetas_emitidas,
            'total_hoy': citas_hoy.count(),
            'pendientes_hoy': pendientes_hoy,
            'rating_promedio': round(rating_promedio, 1),
            'total_valoraciones': total_valoraciones,
            'ultimas_valoraciones': ultimas_valoraciones,
            'critical_alerts': critical_alerts,
            'rating_dist': rating_dist,
            'total_pacientes': pacientes.count(),
            'total_recetas': recetas_emitidas.count(),
        })
    else:
        # Obtenemos el objeto paciente para pasar sus datos al HTML
        paciente = getattr(request.user, 'paciente', None)
        context = {
            'paciente': paciente,
            'edad': paciente.edad if paciente else "N/A",
            'tipo_sangre': paciente.tipo_sangre if paciente else "N/A",
            # Citas futuras/hoy para el dashboard principal
            'citas': paciente.citas.filter(fecha__gte=timezone.now().date()).order_by('fecha', 'hora') if paciente else [],
            'past_citas': paciente.citas.filter(fecha__lt=timezone.now().date()).order_by('-fecha', '-hora') if paciente else [], # Citas pasadas para el historial
            'recetas': paciente.recetas.all().order_by('-fecha') if paciente else [],
        }
        return render(request, 'prototipo.html', context)

def generate_prescription_pdf(receta_id):
    """Función auxiliar para generar el contenido binario del PDF."""
    receta = get_object_or_404(Receta, id=receta_id)
    template_path = 'receta_pdf_template.html'
    context = {'receta': receta}
    
    # Renderizar la plantilla HTML
    template = get_template(template_path)
    html = template.render(context)

    # Crear el archivo PDF en memoria
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

@login_required
@require_POST
def enviar_receta(request, paciente_id):
    if request.user.perfil.tipo != 'medico':
        return JsonResponse({'success': False, 'error': 'No autorizado'})
    
    paciente = get_object_or_404(Paciente, id=paciente_id)
    medicamentos = request.POST.get('medicamentos')
    indicaciones = request.POST.get('indicaciones')
    
    receta = Receta.objects.create(
        paciente=paciente,
        medico=request.user.medico,
        medicamentos=medicamentos,
        indicaciones=indicaciones
    )

    # Generate PDF and save it
    pdf_content = generate_prescription_pdf(receta.id)
    if pdf_content:
        # Save the PDF to the FileField
        receta.pdf_file.save(f'receta_{receta.id}.pdf', ContentFile(pdf_content), save=True)
        
        # Redirect to download the PDF
        return redirect('download_receta_pdf', receta_id=receta.id)
    else:
        # Handle PDF generation error, maybe redirect to dashboard with a message
        return redirect('dashboard') # Or render an error page

@login_required
def download_receta_pdf(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)

    # Basic permission check: only the doctor who created it or the patient it's for
    if request.user.perfil.tipo == 'medico' and receta.medico.user != request.user:
        return HttpResponse("No autorizado para ver esta receta.", status=403)
    if request.user.perfil.tipo == 'paciente' and receta.paciente.user != request.user:
        return HttpResponse("No autorizado para ver esta receta.", status=403)

    if not receta.pdf_file:
        return HttpResponse("El archivo PDF de esta receta no está disponible.", status=404)

    filename = os.path.basename(receta.pdf_file.name)
    response = HttpResponse(receta.pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
@require_POST
def programar_cita(request):
    perfil = request.user.perfil
    fecha = request.POST.get('fecha')
    hora = request.POST.get('hora')
    motivo = request.POST.get('motivo')

    if perfil.tipo == 'paciente':
        paciente = request.user.paciente
        medico = paciente.medico_asignado
        estatus = 'pendiente'
    elif perfil.tipo == 'medico':
        medico = request.user.medico
        paciente_id = request.POST.get('paciente_id')
        try:
            paciente = medico.pacientes.get(id=paciente_id)
        except (Paciente.DoesNotExist, ValueError):
            return redirect('dashboard')
        estatus = 'confirmada'
    else:
        return JsonResponse({'success': False, 'error': 'No autorizado'})

    if not medico:
        return redirect('dashboard')

    # 🔹 Validación de horario laboral (8 AM a 7 PM)
    if hora < '08:00' or hora > '19:00':
        return redirect('dashboard')

    # 🔹 Validación de conflicto de citas (mismo médico, misma fecha y hora)
    if Cita.objects.filter(medico=medico, fecha=fecha, hora=hora).exists():
        return redirect('dashboard')
    
    cita = Cita.objects.create(
        paciente=paciente,
        medico=medico,
        fecha=fecha,
        hora=hora,
        motivo=motivo,
        estatus=estatus
    )
    return redirect('dashboard')

@login_required
@require_POST
def crear_alerta(request):
    """API para que el paciente cree una alerta (manual o automática)"""
    paciente = getattr(request.user, 'paciente', None)
    if not paciente or not paciente.medico_asignado:
        return JsonResponse({'success': False, 'error': 'Paciente o médico no encontrados'})
    
    tipo = request.POST.get('type', 'EMG')
    mensaje = request.POST.get('message', '¡Emergencia! El paciente solicita ayuda inmediata.')
    valor = request.POST.get('value', 'Urgente')
    
    Alerta.objects.create(
        paciente=paciente,
        medico=paciente.medico_asignado,
        type=tipo,
        message=mensaje,
        value=valor,
        resuelto=False
    )
    return JsonResponse({'success': True})

@login_required
@require_POST
def resolver_alerta(request, alert_id):
    """El médico marca la alerta como revisada"""
    if request.user.perfil.tipo != 'medico':
        return JsonResponse({'success': False, 'error': 'No autorizado'})
    
    alerta = get_object_or_404(Alerta, id=alert_id, medico=request.user.medico)
    alerta.resuelto = True
    alerta.save()
    return JsonResponse({'success': True, 'message': 'Alerta resuelta'})

 #MUCHAS DUDAS AQUÍ-----------------------------------------------

@login_required
def perfil_medico_view(request):
    # Asegurarse de que solo los médicos puedan acceder a esta vista
    if request.user.perfil.tipo != 'medico':
        return redirect('dashboard') 

    medico = request.user.medico

    if request.method == 'POST':
        # Actualizar los campos del médico con los datos del formulario
        medico.nombre = request.POST.get('nombre', medico.nombre).strip()
        medico.especialidad = request.POST.get('especialidad', medico.especialidad).strip()
        medico.telefono = request.POST.get('telefono', medico.telefono).strip()
        medico.direccion = request.POST.get('direccion', medico.direccion).strip()
        medico.cedula = request.POST.get('cedula', medico.cedula).strip()
        medico.cp = request.POST.get('cp', medico.cp).strip()
        medico.estado = request.POST.get('estado', medico.estado).strip()
        medico.municipio = request.POST.get('municipio', medico.municipio).strip()
        medico.colonia = request.POST.get('colonia', medico.colonia).strip()

        # Procesar foto si se subió una nueva
        if request.FILES.get('foto'):
            medico.foto = request.FILES.get('foto')

        medico.save()
        # Opcional: Actualizar el nombre del usuario de Django si el nombre del médico es el nombre completo
        request.user.first_name = medico.nombre
        request.user.save()
        return redirect('perfil_medico') # Redirigir a la misma página para mostrar los cambios

    return render(request, 'perfil_medico.html', {'medico': medico})

# 🔹 API PARA VALIDAR CÓDIGO POSTAL
def buscar_cp(request):
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

@login_required
@require_POST
def valorar_medico(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente__user=request.user)
    puntuacion = request.POST.get('puntuacion')
    comentario = request.POST.get('comentario', '')

    Valoracion.objects.update_or_create(
        cita=cita,
        defaults={'paciente': cita.paciente, 'medico': cita.medico, 'puntuacion': puntuacion, 'comentario': comentario}
    )
    return redirect('dashboard')
