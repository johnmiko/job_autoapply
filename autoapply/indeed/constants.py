import os
from pathlib import Path

INDEED_DIR = os.path.dirname(os.path.abspath(Path(__file__)))
AUTOAPPLY_DIR = os.path.dirname(os.path.abspath(Path(__file__).parent))
PROJ_DIR = os.path.dirname(os.path.abspath(Path(__file__).parent.parent))

STATS_FILENAME = INDEED_DIR + '/text/stats.txt'
JOB_NUMBER_FILENAME = INDEED_DIR + '/text/job_number.txt'


class Page:
    pass
