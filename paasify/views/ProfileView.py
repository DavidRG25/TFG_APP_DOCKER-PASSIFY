# paasify/views/ProfileView.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.http import JsonResponse
from paasify.models.StudentModel import UserProfile
from paasify.models.SubjectModel import Subject


@login_required
def profile_view(request):
    """
    Vista principal del perfil de usuario.
    Muestra datos personales, asignaturas y token API.
    """
    user = request.user
    
    # Obtener o crear UserProfile
    try:
        profile = user.user_profile
    except UserProfile.DoesNotExist:
        profile = None
    
    # Obtener token de API (ExpiringToken)
    api_token_data = None
    try:
        from paasify.models.TokenModel import ExpiringToken
        token = ExpiringToken.objects.get(user=user)
        api_token_data = {
            'key': token.key,
            'masked': f"...{token.key[-8:]}",
            'created': token.created,
            'expires_at': token.expires_at,
            'days_remaining': token.days_until_expiration(),
            'is_expired': token.is_expired(),
        }
    except ExpiringToken.DoesNotExist:
        pass
    
    # Obtener asignaturas segun rol
    subjects_as_student = []
    subjects_as_teacher = []
    
    if user.groups.filter(name__iexact='student').exists():
        subjects_as_student = Subject.objects.filter(students=user)
    
    if user.groups.filter(name__iexact='teacher').exists():
        subjects_as_teacher = Subject.objects.filter(teacher_user=user)
    
    is_admin = user.is_superuser
    is_teacher = user.groups.filter(name__iexact='teacher').exists()
    is_student = user.groups.filter(name__iexact='student').exists()
    
    # Jerarquia de roles para no duplicar en el perfil si no es necesario: Admin > Teacher > Student
    display_student = is_student and not is_teacher and not is_admin
    display_teacher = is_teacher and not is_admin
    
    # Estadísticas para el perfil
    from containers.models import Service
    from paasify.models.ProjectModel import UserProject
    
    if is_admin:
        stats = {
            'projects': UserProject.objects.count(),
            'services': Service.objects.exclude(status='removed').count(),
            'subjects': Subject.objects.count()
        }
    elif is_teacher:
        # Alumnos únicos en las asignaturas del profesor
        from django.contrib.auth.models import User
        unique_students_count = User.objects.filter(subjects_as_student__in=subjects_as_teacher).distinct().count()
        stats = {
            'students': unique_students_count,
            'projects': UserProject.objects.filter(subject__teacher_user=user).count(),
            'subjects': Subject.objects.filter(teacher_user=user).count()
        }
    else:
        stats = {
            'projects': UserProject.objects.filter(user_profile__user=user).count(),
            'services': Service.objects.filter(owner=user).exclude(status='removed').count(),
            'subjects': Subject.objects.filter(students=user).count()
        }

    context = {
        'user': user,
        'profile': profile,
        'api_token': api_token_data,
        'subjects_as_student': subjects_as_student,
        'subjects_as_teacher': subjects_as_teacher,
        'is_student': display_student,
        'is_teacher': display_teacher,
        'is_admin': is_admin,
        'stats': stats,
    }
    
    return render(request, 'profile.html', context)


@login_required
def change_password_view(request):
    """
    Procesa el cambio de contrasena del usuario.
    """
    if request.method == 'POST':
        is_force_change = request.POST.get('force_change') == 'true'
        user_must_change = hasattr(request.user, 'user_profile') and request.user.user_profile.must_change_password
        
        if is_force_change and user_must_change:
            form = SetPasswordForm(request.user, request.POST)
        else:
            form = PasswordChangeForm(request.user, request.POST)
            
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener sesion activa
            
            # Limpiar el flag si estaba activo
            if hasattr(user, 'user_profile'):
                user.user_profile.must_change_password = False
                user.user_profile.save()
            
            messages.success(request, 'Tu contrasena ha sido cambiada exitosamente.')
            return redirect('profile')
        else:
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)
    
    return redirect('profile')


@login_required
def generate_token_view(request):
    """
    Genera un nuevo token de API con expiración de 30 días.
    Retorna el token completo en JSON.
    """
    if request.method == 'POST':
        user = request.user
        
        # Importar ExpiringToken
        from paasify.models.TokenModel import ExpiringToken
        
        # Generar token (eliminar el anterior si existe y crear uno nuevo)
        try:
            # Eliminar token anterior si existe
            ExpiringToken.objects.filter(user=user).delete()
            
            # Crear nuevo token
            token = ExpiringToken.objects.create(user=user)
            
            return JsonResponse({
                'success': True,
                'token': token.key,
                'created_at': token.created.isoformat(),
                'expires_at': token.expires_at.isoformat(),
                'days_remaining': token.days_until_expiration(),
                'message': 'Token generado exitosamente. Válido por 30 días. Cópialo ahora, no podrás verlo completo después.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al generar token: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'}, status=405)


@login_required
def refresh_token_view(request):
    """
    Regenera el token de API del usuario con caducidad de 30 días.
    Retorna el nuevo token completo en JSON.
    """
    if request.method == 'POST':
        user = request.user
        
        # Importar ExpiringToken
        from paasify.models.TokenModel import ExpiringToken
        
        # Refrescar token (eliminar el anterior y crear uno nuevo)
        try:
            ExpiringToken.objects.filter(user=user).delete()
            token = ExpiringToken.objects.create(user=user)
            
            return JsonResponse({
                'success': True,
                'token': token.key,
                'created_at': token.created.isoformat(),
                'expires_at': token.expires_at.isoformat(),
                'days_remaining': token.days_until_expiration(),
                'message': 'Token refrescado exitosamente. Válido por 30 días. El token anterior ya no es válido.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al refrescar token: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'}, status=405)


@login_required
def copy_token_view(request):
    """
    Retorna el token completo del usuario para copiarlo.
    """
    if request.method == 'GET':
        user = request.user
        
        try:
            from paasify.models.TokenModel import ExpiringToken
            token = ExpiringToken.objects.get(user=user)
            return JsonResponse({
                'success': True,
                'token': token.key
            })
        except ExpiringToken.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No tienes un token generado. Por favor, genera uno nuevo.'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'}, status=405)


@login_required
def update_profile_view(request):
    """
    Actualiza los datos básicos del perfil (Email y Nombre Completo).
    """
    if request.method == 'POST':
        user = request.user
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        
        # 1. Validar email (si cambia)
        if email and email != user.email:
            from django.contrib.auth.models import User
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, 'Este correo electrónico ya está en uso por otra cuenta.')
                return redirect('profile')
            user.email = email
            user.save()
            
        # 2. Validar nombre completo en UserProfile
        if full_name:
            try:
                profile = user.user_profile
                profile.nombre = full_name
                profile.save()
            except UserProfile.DoesNotExist:
                # Si por alguna razón no tiene perfil, lo creamos
                UserProfile.objects.create(user=user, nombre=full_name)
                
        messages.success(request, 'Tus datos de perfil han sido actualizados.')
        
    return redirect('profile')
