import sys
import logging

#logger = logging.getLogger("clovek-ne-jezi-se")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)
#logger.addHandler(handler)
#logger.propagate = True
