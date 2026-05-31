import uuid


def gen_id() -> str:
    """Genera un ID corto único de 8 caracteres."""
    return str(uuid.uuid4()).replace("-", "")[:8].upper()
