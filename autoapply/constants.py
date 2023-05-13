##### Settings - Start #####
import logging
import os
from pathlib import Path

GLOBAL_LOG_LEVEL = logging.INFO
AUTOAPPLY_DIR = os.path.dirname(os.path.abspath(Path(__file__)))
PROJ_DIR = os.path.dirname(os.path.abspath(Path(__file__).parent))
