"""
FastAPI Performance Logging Middleware

This module provides middleware for logging FastAPI request performance metrics.

Usage:
    from lotkeeper.common.middlewares import add_performance_middleware

    # Add to your FastAPI app
    add_performance_middleware(
        app,
        log_slow_requests=True,
        slow_request_threshold=1.0,
        log_all_requests=True,
        exclude_paths={"/health", "/metrics"},
    )

    # Or add middleware directly
    from lotkeeper.common.middlewares import PerformanceLoggingMiddleware

    app.add_middleware(PerformanceLoggingMiddleware)
"""

import time
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for logging request performance metrics.

    This middleware logs:
    - Request method and path
    - Response status code
    - Request processing time
    - Request size (if available)
    - Response size (if available)
    - Query parameters count
    """

    def __init__(
        self,
        app: ASGIApp,
        log_slow_requests: bool = True,
        slow_request_threshold: float = 1.0,
        log_all_requests: bool = True,
        exclude_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.log_slow_requests = log_slow_requests
        self.slow_request_threshold = slow_request_threshold
        self.log_all_requests = log_all_requests
        self.exclude_paths = exclude_paths or {"/health", "/metrics", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Extract request information
        method = request.method
        path = request.url.path
        query_params_count = len(request.query_params)
        user_agent = request.headers.get("user-agent", "unknown")

        # Get request size if available
        content_length = request.headers.get("content-length")
        request_size = int(content_length) if content_length else 0

        try:
            # Process the request
            response = await call_next(request)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Get response size if available
            response_size = self._get_response_size(response)

            # Determine log level based on performance and status
            log_level = self._determine_log_level(processing_time, response.status_code)

            # Log the request
            self._log(
                method=method,
                path=path,
                status_code=response.status_code,
                processing_time=processing_time,
                query_params_count=query_params_count,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                log_level=log_level,
            )

            return response

        except Exception as e:
            # Log errors with timing information
            processing_time = time.time() - start_time
            logger.error(f"Request failed: {method} {path} - Error: {e!s} - Time: {processing_time:.3f}s")
            raise

    def _get_response_size(self, response: Response) -> int:
        """Get response size in bytes if available."""
        content_length = response.headers.get("content-length")
        if content_length:
            return int(content_length)

        # For streaming responses or when content-length is not set
        return 0

    def _determine_log_level(self, processing_time: float, status_code: int) -> str:
        """Determine appropriate log level based on performance and status."""
        # Error status codes
        if status_code >= HTTP_500_INTERNAL_SERVER_ERROR:
            return "ERROR"
        elif status_code >= HTTP_400_BAD_REQUEST:
            return "WARNING"

        # Slow requests
        if self.log_slow_requests and processing_time >= self.slow_request_threshold:
            return "WARNING"

        # Normal requests
        return "INFO"

    def _log(
        self,
        method: str,
        path: str,
        status_code: int,
        processing_time: float,
        query_params_count: int,
        request_size: int,
        response_size: int,
        user_agent: str,
        log_level: str,
    ) -> None:
        """Log the request with performance metrics."""
        if not self.log_all_requests and log_level == "INFO":
            return

        # Format the log message
        log_message = (
            f"{method} {path} - Status: HTTP/{status_code} - Time: {processing_time:.3f}s - User-Agent: {user_agent}"
        )

        # Add additional context for detailed logging
        context = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "processing_time": processing_time,
            "query_params_count": query_params_count,
            "request_size_bytes": request_size,
            "response_size_bytes": response_size,
            "user_agent": user_agent,
        }

        # Log with appropriate level
        if log_level == "ERROR":
            logger.error(log_message, extra=context)
        elif log_level == "WARNING":
            logger.warning(log_message, extra=context)
        else:
            logger.info(log_message, extra=context)


def add_performance_middleware(
    app: Any,
    log_slow_requests: bool = True,
    slow_request_threshold: float = 1.0,
    log_all_requests: bool = True,
    exclude_paths: set[str] | None = None,
) -> None:
    """Convenience function to add performance logging middleware to FastAPI app.

    Args:
        app: FastAPI application instance
        log_slow_requests: Whether to log slow requests with WARNING level
        slow_request_threshold: Threshold in seconds for considering a request slow
        log_all_requests: Whether to log all requests or only slow/error requests
        exclude_paths: Set of paths to exclude from logging
    """
    # Add performance logging middleware
    app.add_middleware(
        PerformanceLoggingMiddleware,
        log_slow_requests=log_slow_requests,
        slow_request_threshold=slow_request_threshold,
        log_all_requests=log_all_requests,
        exclude_paths=exclude_paths,
    )
