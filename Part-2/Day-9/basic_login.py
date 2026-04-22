import logging

logger = logging.getLogger("myapp.orders")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
fmt = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
handler.setFormatter(fmt)
logger.addHandler(handler)

# Add context with extra=
logger.info(
    "order_placed",
    extra={"order_id": "ord_123", "amount": 49.99}
)