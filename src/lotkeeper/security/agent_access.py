# ... existing code ...

from http import HTTPStatus

from fastapi import HTTPException, Request
from loguru import logger

from lotkeeper.config import ENV

X_AGENT_ACCESS_TOKEN_HEADER = "X-Agent-Access-Token"


def verify_agent_access_token(request: Request) -> bool:
    """Dependency to verify agent access token for specific routes"""

    if ENV.is_dev():
        logger.warning("Notice: allowing agent request to go through in development without a token")
        return True

    try:
        agent_token = request.headers.get(X_AGENT_ACCESS_TOKEN_HEADER)

        if not agent_token:
            logger.warning("Agent token missing")
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Malformed request, missing required header",
            )

        if agent_token != ENV.LOT_AGENT_TOKEN:
            logger.warning("Agent token invalid")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid agent access token")

        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during agent authentication: {e}", exc_info=True)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Unexpected error during agent authentication"
        ) from e
