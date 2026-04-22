import logging

logger = logging.getLogger(__name__)


def init_sentry(sentry_dsn: str | None, environment: str = "development", release: str | None = None) -> None:
    """Initialize Sentry SDK. No-op when sentry_dsn is not set."""
    if not sentry_dsn:
        logger.info("Sentry DSN not configured — error tracking disabled")
        return

    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=release,
        traces_sample_rate=1.0 if environment != "production" else 0.1,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
        ],
        send_default_pii=False,
    )
    logger.info("Sentry initialized", extra={"environment": environment})
