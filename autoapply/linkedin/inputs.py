from autoapply.linkedin.constants import LINKEDIN_DIR

# True, False
job_number = 0
# job_number = 15
USE_MAX_TIMER = True
# USE_MAX_TIMER = False
ONLY_PYTHON_JOBS = False
STOP_AFTER_EVERY_JOB = True
# STOP_AFTER_EVERY_JOB = True
PAUSE_AFTER_FAILURE = True
PAUSE_AFTER_ANSWERING_QUESTIONS = True
# Test Automation USA
base_urls = [
    "https://www.linkedin.com/jobs/search/?currentJobId=3840550772&f_AL=true&f_WT=2&geoId=103644278&keywords=test%20automation&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
]
TEXT_DIR = LINKEDIN_DIR + '/text/'
APPLIED_FOR_FILE = f'{TEXT_DIR}applied_for.csv'
ERROR_FILE = f'{TEXT_DIR}errors.txt'
question_file = f'{TEXT_DIR}questions.txt'
unanswered_question_file = f'{TEXT_DIR}unanswered_questions.txt'
SECONDS_TO_TRY_FOR = 90
