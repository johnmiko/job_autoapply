# True, False
from autoapply.linkedin.constants import LINKEDIN_DIR

USE_MAX_TIMER = True
# USE_MAX_TIMER = False
ONLY_PYTHON_JOBS = False
STOP_AFTER_EVERY_JOB = False
# STOP_AFTER_EVERY_JOB = True
PAUSE_AFTER_FAILURE = False
PAUSE_AFTER_ANSWERING_QUESTIONS = False
START_AT_JOB_NUMBER_X = 3  # Set to any number besides -1, to override what job number is started at
# Test Automation USA
base_urls = [
    "https://www.linkedin.com/jobs/search/?currentJobId=3840550772&f_AL=true&f_WT=2&geoId=103644278&keywords=test%20automation&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
]
DO_NOT_APPLY_AT_THESE_COMPANIES = ['smartd']  # put in your current company
TEXT_DIR = "D:/Users/johnm/OneDrive/ccode_files/job_autoapply/linkedin/text/"
if not TEXT_DIR:
    TEXT_DIR = LINKEDIN_DIR + '/text/'
APPLIED_FOR_FILE = f'{TEXT_DIR}applied_for.csv'
ERROR_FILE = f'{TEXT_DIR}errors.txt'
STATS_FILENAME = f"{TEXT_DIR}stats.txt"
JOB_NUMBER_FILENAME = f"{TEXT_DIR}job_number.txt"
COMPLETED_FILENAME = f"{TEXT_DIR}completed.txt"
question_file = f'{TEXT_DIR}questions.txt'
unanswered_question_file = f'{TEXT_DIR}unanswered_questions.txt'
SECONDS_TO_TRY_FOR = 90
