"""
Utilidades para generar contraseñas seguras.
"""
import secrets
import string


def generate_password(length=12):
    """
    Genera una contraseña aleatoria segura.
    
    Args:
        length (int): Longitud de la contraseña (default: 12)
    
    Returns:
        str: Contraseña generada
    
    Ejemplo:
        >>> password = generate_password()
        >>> len(password)
        12
        >>> password = generate_password(16)
        >>> len(password)
        16
    """
    # Alfabeto: letras mayúsculas, minúsculas, dígitos y caracteres especiales seguros
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    
    # Generar contraseña aleatoria
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    
    # Asegurar que tenga al menos una mayúscula, una minúscula, un dígito y un carácter especial
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%" for c in password)
    
    # Si no cumple los requisitos, regenerar
    if not (has_upper and has_lower and has_digit and has_special):
        return generate_password(length)
    
    return password
