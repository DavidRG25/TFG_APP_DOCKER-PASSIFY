"""Señales para mantener sincronizado el modelo Player con los grupos."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .roles import ensure_player_profile, user_is_student

User = get_user_model()


@receiver(m2m_changed, sender=User.groups.through)
def sync_player_on_group_change(sender, instance, action, **kwargs):
    if action != "post_add":
        return
    if getattr(instance, "_skip_player_autocreate", False):
        return
    if user_is_student(instance):
        ensure_player_profile(instance)

