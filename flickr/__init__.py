import logging
import sys

logger = logging.getLogger("flickr_backup")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)
