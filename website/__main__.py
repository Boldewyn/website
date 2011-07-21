#!/usr/bin/python
""""""


import logging
import sys
import traceback
from website._webtools.build import build


logger = logging.getLogger("website")


def main():
    """"""
    return build()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logger.critical(traceback.format_exc())
        sys.exit(1)

