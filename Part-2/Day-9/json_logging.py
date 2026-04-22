import json, logging
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """Emit one JSON object per log record."""

    BASE_FIELDS = {"name", "levelname", "pathname",
                   "lineno", "args", "exc_info", "exc_text"}

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "file": f"{record.pathname}:{record.lineno}",
        }
        # Merge any extra= fields
        extras = {k: v for k, v in record.__dict__.items()
                  if k not in logging.LogRecord.__dict__
                  and k not in self.BASE_FIELDS}
        payload.update(extras)

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)
    

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("myapp")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info(
    "payment_processed",
    extra={
        "user_id": "u_42",
        "amount_usd": 129.00,
        "method": "card",
        "trace_id": "abc-123",
    }
)