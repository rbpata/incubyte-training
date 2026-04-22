import logging

class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.setLevel(logging.INFO)
        handler = logging.FileHandler("log.log", mode="w")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def info(self, message):
        super().info(message)

    def warning(self, message):
        super().warning(message)

    def error(self, message):
        super().error(message)

logger = Logger(__name__)


def main():
    logger.info("Starting the main function.")
    logger.info("Finished the main function.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    


