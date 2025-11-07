"""Helpers para gestionar roles y grupos coherentes en PaaSify."""
from __future__ import annotations

from typing import Iterable, Optional

from django.contrib.auth.models import Group
from django.db import transaction

# Listas de nombres aceptados para cada rol (sensibles a mayúsculas/minúsculas).
STUDENT_GROUP_NAMES: tuple[str, ...] = ("alumno", "Alumno", "student", "Student")
TEACHER_GROUP_NAMES: tuple[str, ...] = ("profesor", "Profesor", "teacher", "Teacher")

DEFAULT_STUDENT_GROUP = "Student"
DEFAULT_TEACHER_GROUP = "Teacher"


def _pick_existing_group(candidate_names: Iterable[str]) -> Optional[Group]:
    for name in candidate_names:
        try:
            return Group.objects.get(name__iexact=name)
        except Group.DoesNotExist:
            continue
    return None


def _ensure_group(name: str) -> Group:
    group, _ = Group.objects.get_or_create(name=name)
    return group


def ensure_user_group(user, candidate_names: Iterable[str], fallback: str) -> Group:
    """Garantiza que el usuario pertenezca al menos a un grupo de la lista indicada."""
    group = _pick_existing_group(candidate_names)
    if group is None:
        group = _ensure_group(fallback)
    user.groups.add(group)
    return group


def user_has_group(user, names: Iterable[str]) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    return any(user.groups.filter(name__iexact=name).exists() for name in names)


def user_is_student(user) -> bool:
    return user_has_group(user, STUDENT_GROUP_NAMES)


def user_is_teacher(user) -> bool:
    return user_has_group(user, TEACHER_GROUP_NAMES)


def user_is_admin(user) -> bool:
    return getattr(user, "is_superuser", False) or getattr(user, "is_staff", False)


@transaction.atomic
def ensure_user_profile(user) -> "UserProfile":
    """Crea (si no existe) el perfil ``UserProfile`` enlazado al usuario."""
    from paasify.models.StudentModel import UserProfile

    profile, created = UserProfile.objects.get_or_create(user=user, defaults={})
    if not created:
        return profile

    nombre_base = (user.get_full_name() or user.username or user.email or f"alumno-{user.pk}").strip()
    if not nombre_base:
        nombre_base = f"alumno-{user.pk}"

    unique_name = nombre_base
    suffix = 1
    while UserProfile.objects.filter(nombre=unique_name).exclude(pk=profile.pk).exists():
        suffix += 1
        unique_name = f"{nombre_base}-{suffix}"

    email = user.email or f"{user.username or 'alumno'}@pendiente.local"
    sexo = "Masculino"

    profile.nombre = unique_name
    profile.year = email
    profile.sexo = sexo
    profile.save()
    return profile
