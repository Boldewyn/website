

import logging


logger = logging.getLogger("website")
logger.addHandler(logging.StreamHandler())


VERSION = (1, 1)

def get_version():
    return ".".join(map(lambda i: str(i), VERSION))
