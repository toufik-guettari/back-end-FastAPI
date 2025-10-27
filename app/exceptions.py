"""Exceptions personnalisées pour l'application."""


class AppException(Exception):
    """Exception de base pour l'application."""
    
    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(AppException):
    """Ressource non trouvée."""
    pass


class AlreadyExistsError(AppException):
    """Ressource existe déjà."""
    pass


class ValidationError(AppException):
    """Erreur de validation métier."""
    pass


class DatabaseError(AppException):
    """Erreur base de données."""
    pass