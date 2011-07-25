

import logging


logger = logging.getLogger("website")
_handler = logging.StreamHandler()
_formatter = logging.Formatter("[%(levelname)s] %(message)s - %(name)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)


VERSION = (1, 1)

def get_version():
    return ".".join(map(lambda i: str(i), VERSION))
