import sys
import logging

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
)
handler.setFormatter(formatter)
