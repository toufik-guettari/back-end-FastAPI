"""Middleware pour générer request_id unique par requête."""
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Ajoute un request_id unique à chaque requête."""
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        request_id = str(uuid.uuid4())
        
        # Ajouter request_id au context Loguru
        with logger.contextualize(request_id=request_id):
            # Logger la requête
            logger.info(
                f"{request.method} {request.url.path}",
                extra={"method": request.method, "path": request.url.path}
            )
            
            # Traiter la requête
            response = await call_next(request)
            
            # Ajouter header dans réponse
            response.headers["X-Request-ID"] = request_id
            
            # Logger la réponse
            logger.info(
                f"Response {response.status_code}",
                extra={"status_code": response.status_code}
            )
            
            return response