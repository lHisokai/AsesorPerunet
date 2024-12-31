import re

def validate_email(email: str):
    """
    Valida un correo electrónico.
    :param email: str
    :return: bool
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None
