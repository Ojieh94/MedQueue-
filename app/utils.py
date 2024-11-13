import re


def validate_password(password: str, first_name: str, last_name: str) -> str:
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if first_name.lower() in password.lower() or last_name.lower() in password.lower():
        return "Password cannot be the same as your name"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    if ' ' in password:
        return "Password must not contain spaces"
    return "Password is valid"
