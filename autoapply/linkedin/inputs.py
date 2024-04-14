# True, False
import ast

from dotenv import dotenv_values

from autoapply.linkedin.constants import LINKEDIN_DIR

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
USE_MAX_TIMER = ast.literal_eval(config["USE_MAX_TIMER"])
# USE_MAX_TIMER = False
JOB_MUST_CONTAIN = config["JOB_MUST_CONTAIN"]
STOP_AFTER_EVERY_JOB = ast.literal_eval(config["STOP_AFTER_EVERY_JOB"])
# STOP_AFTER_EVERY_JOB = True
PAUSE_AFTER_FAILURE = ast.literal_eval(config["PAUSE_AFTER_FAILURE"])
PAUSE_AFTER_ANSWERING_QUESTIONS = ast.literal_eval(config["PAUSE_AFTER_ANSWERING_QUESTIONS"])
START_AT_JOB_NUMBER_X = int(config["START_AT_JOB_NUMBER_X"])
GUESS_0_FOR_UNANSWERED = ast.literal_eval(config["GUESS_0_FOR_UNANSWERED"])
# Test Automation USA
base_urls = [
    "https://www.linkedin.com/jobs/search/?f_AL=true&f_WT=2&geoId=103644278&keywords=test%20automation&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
]
DO_NOT_APPLY_AT_THESE_COMPANIES = ['smartd']  # put in your current company
TEXT_DIR = "D:/Users/johnm/OneDrive/ccode_files/job_autoapply/linkedin/text/"
if not TEXT_DIR:
    TEXT_DIR = LINKEDIN_DIR + '/text/'
APPLIED_FOR_FILE = f'{TEXT_DIR}applied_for.csv'
ERROR_FILE = f'{TEXT_DIR}errors.txt'
STATS_FILENAME = f"{TEXT_DIR}stats.txt"
JOB_NUMBER_FILENAME = f"{TEXT_DIR}job_number.txt"
question_file = f'{TEXT_DIR}questions.txt'
unanswered_question_file = f'{TEXT_DIR}unanswered_questions.txt'
REFERENCES_FILE = f'{TEXT_DIR}references.txt'
SECONDS_TO_TRY_FOR = 90
