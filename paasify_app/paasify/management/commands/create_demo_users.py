"""Create default admin, student, and professor users for local environments."""
from __future__ import annotations

import os
from typing import Iterable, Optional

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from paasify import roles


class Command(BaseCommand):
    help = (
        "Create or update demo users: admin, "
        "student (Alumno!2025) and professor (Profesor!2025). "
        "The admin password can be overridden via the ADMIN_PASSWORD env variable."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        # Allow overriding the admin password via environment variable
        admin_password = os.environ.get("ADMIN_PASSWORD", "Admin!123")
        if admin_password != "Admin!123":
            self.stdout.write(
                self.style.WARNING("  → Using ADMIN_PASSWORD from environment variable.")
            )

        users_config: Iterable[dict[str, object]] = (
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": admin_password,
                "is_staff": True,
                "is_superuser": True,
                "group": None,
            },
            {
                "username": "alumno",
                "email": "alumno@example.com",
                "password": "Alumno!2025",
                "is_staff": False,
                "is_superuser": False,
                "group": "student",
            },
            {
                "username": "profesor",
                "email": "profesor@example.com",
                "password": "Profesor!2025",
                "is_staff": False,
                "is_superuser": False,
                "group": "teacher",
            },
        )

        for config in users_config:
            username = config["username"]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": config["email"],
                    "is_staff": config["is_staff"],
                    "is_superuser": config["is_superuser"],
                },
            )

            updated_flags = []
            if not created:
                # Sync staff and superuser flags with the desired configuration.
                for flag in ("is_staff", "is_superuser"):
                    desired = config[flag]
                    if getattr(user, flag) != desired:
                        setattr(user, flag, desired)
                        updated_flags.append(flag)

                if user.email != config["email"]:
                    user.email = config["email"]
                    updated_flags.append("email")

            user.set_password(config["password"])
            user.save()

            role = config["group"]
            if role == "student":
                roles.ensure_user_group(
                    user,
                    roles.STUDENT_GROUP_NAMES,
                    roles.DEFAULT_STUDENT_GROUP,
                )
                roles.ensure_user_profile(user)
            elif role == "teacher":
                roles.ensure_user_group(
                    user,
                    roles.TEACHER_GROUP_NAMES,
                    roles.DEFAULT_TEACHER_GROUP,
                )
                roles.ensure_user_profile(user)

            action = "created" if created else "updated"
            extras: list[str] = []
            if updated_flags:
                extras.append(f"sync flags: {', '.join(updated_flags)}")
            if role:
                extras.append(f"role={role}")

            extra_msg = f" ({'; '.join(extras)})" if extras else ""
            self.stdout.write(
                self.style.SUCCESS(f"- User '{username}' {action}{extra_msg}")
            )

        self.stdout.write(self.style.SUCCESS("Demo users ready."))
