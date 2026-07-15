"""
VibeGuard security middleware for JWT validation, rate limiting, and threat logging.
Provides centralized security controls and suspicious activity detection.
"""
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.utils.jwt_handler import JWTHandler
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class VibeGuardMiddleware(BaseHTTPMiddleware):
    """
    Security middleware that validates JWT tokens, logs requests,
    and detects suspicious activity patterns.
    """

    # Routes that don't require authentication
    PUBLIC_ROUTES = {
        "/",
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
    }

    async def dispatch(self, request: Request, call_next):
        """
        Process each request through security checks.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response from handler or security error
        """
        # Extract request metadata for logging
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        path = request.url.path

        # Log incoming request
        logger.debug(
            f"Request: {request.method} {path} from {client_ip} | UA: {user_agent}"
        )

        # Skip auth for public routes
        if self._is_public_route(path):
            return await call_next(request)

        # Validate JWT token for protected routes
        try:
            token = self._extract_token(request)

            if not token:
                return self._create_error_response(
                    "Missing authentication token",
                    status.HTTP_401_UNAUTHORIZED,
                    client_ip,
                    path
                )

            # Verify token and add user context to request
            payload = JWTHandler.verify_access_token(token)

            if not payload:
                return self._create_error_response(
                    "Invalid or expired token",
                    status.HTTP_401_UNAUTHORIZED,
                    client_ip,
                    path
                )

            # Attach user info to request state for route handlers
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")

            # Check for suspicious patterns
            self._check_suspicious_activity(request, payload, client_ip)

        except Exception as e:
            logger.error(f"VibeGuard error processing request: {e}")
            return self._create_error_response(
                "Authentication failed",
                status.HTTP_401_UNAUTHORIZED,
                client_ip,
                path
            )

        # Pass to next handler
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

    def _is_public_route(self, path: str) -> bool:
        """Check if route is public (no auth required)."""
        return any(path.startswith(route) for route in self.PUBLIC_ROUTES)

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Args:
            request: HTTP request

        Returns:
            Token string if found, None otherwise
        """
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        # Expected format: "Bearer <token>"
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Malformed Authorization header: {auth_header}")
            return None

        return parts[1]

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address, accounting for proxies.

        Args:
            request: HTTP request

        Returns:
            Client IP address string
        """
        # Check X-Forwarded-For header (set by proxies/load balancers)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take first IP in chain (original client)
            return forwarded.split(",")[0].strip()

        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"

    def _check_suspicious_activity(
            self,
            request: Request,
            payload: dict,
            client_ip: str
    ) -> None:
        """
        Analyze request for suspicious patterns.
        Logs warnings but doesn't block (for monitoring/alerting).

        Args:
            request: HTTP request
            payload: Decoded JWT payload
            client_ip: Client IP address
        """
        user_id = payload.get("sub")

        # Check for token about to expire (possible attack indicator)
        exp = payload.get("exp", 0)
        import time
        time_to_expire = exp - time.time()

        if time_to_expire < 60:  # Less than 1 minute
            logger.warning(
                f"Token near expiry used | User: {user_id} | IP: {client_ip}"
            )

        # Check for unusual user agent strings (potential bot)
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning(
                f"Suspicious user agent | User: {user_id} | IP: {client_ip} | UA: {user_agent}"
            )

        # Log high-value operations
        if request.method in ["DELETE", "PUT"] or "admin" in request.url.path:
            logger.info(
                f"High-value operation | User: {user_id} | IP: {client_ip} | "
                f"Method: {request.method} | Path: {request.url.path}"
            )

    def _create_error_response(
            self,
            message: str,
            status_code: int,
            client_ip: str,
            path: str
    ) -> JSONResponse:
        """
        Create standardized error response and log security event.

        Args:
            message: Error message
            status_code: HTTP status code
            client_ip: Client IP address
            path: Request path

        Returns:
            JSONResponse with error details
        """
        logger.warning(
            f"Security rejection | IP: {client_ip} | Path: {path} | Reason: {message}"
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": message,
                "data": None
            }
        )


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: HTTP request
        exc: Rate limit exception

    Returns:
        JSON error response
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.warning(f"Rate limit exceeded | IP: {client_ip} | Path: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "status": "error",
            "message": "Rate limit exceeded. Please try again later.",
            "data": None
        }
    )