# paasify/views/ProfileView.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
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
    
    # Obtener asignaturas segun rol
    subjects_as_student = []
    subjects_as_teacher = []
    
    if user.groups.filter(name__iexact='student').exists():
        subjects_as_student = Subject.objects.filter(students=user)
    
    if user.groups.filter(name__iexact='teacher').exists():
        subjects_as_teacher = Subject.objects.filter(teacher_user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'subjects_as_student': subjects_as_student,
        'subjects_as_teacher': subjects_as_teacher,
        'is_student': user.groups.filter(name__iexact='student').exists(),
        'is_teacher': user.groups.filter(name__iexact='teacher').exists(),
    }
    
    return render(request, 'profile.html', context)


@login_required
def change_password_view(request):
    """
    Procesa el cambio de contrasena del usuario.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener sesion activa
            messages.success(request, 'Tu contrasena ha sido cambiada exitosamente.')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('profile')


@login_required
def generate_token_view(request):
    """
    Genera un nuevo token JWT para el usuario.
    Retorna el token completo en JSON.
    """
    if request.method == 'POST':
        user = request.user
        
        # Verificar que el usuario tenga UserProfile
        try:
            profile = user.user_profile
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No tienes un perfil asociado. Contacta al administrador.'
            }, status=400)
        
        # Generar token
        try:
            token = profile.generate_token(expiration_days=365)
            return JsonResponse({
                'success': True,
                'token': token,
                'masked_token': profile.get_masked_token(),
                'created_at': profile.token_created_at.isoformat() if profile.token_created_at else None,
                'message': 'Token generado exitosamente. Copialo ahora, no podras verlo completo despues.'
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
    Regenera el token JWT del usuario (invalida el anterior).
    Retorna el nuevo token completo en JSON.
    """
    if request.method == 'POST':
        user = request.user
        
        # Verificar que el usuario tenga UserProfile
        try:
            profile = user.user_profile
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No tienes un perfil asociado. Contacta al administrador.'
            }, status=400)
        
        # Refrescar token
        try:
            token = profile.refresh_token(expiration_days=365)
            return JsonResponse({
                'success': True,
                'token': token,
                'masked_token': profile.get_masked_token(),
                'created_at': profile.token_created_at.isoformat() if profile.token_created_at else None,
                'message': 'Token refrescado exitosamente. El token anterior ya no es valido.'
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
        
        # Verificar que el usuario tenga UserProfile
        try:
            profile = user.user_profile
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No tienes un perfil asociado.'
            }, status=400)
        
        if not profile.api_token:
            return JsonResponse({
                'success': False,
                'error': 'No tienes un token generado. Genera uno primero.'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'token': profile.api_token
        })
    
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'}, status=405)
