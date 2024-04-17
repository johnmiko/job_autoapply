# True, False
import ast

from dotenv import dotenv_values

from autoapply.linkedin.constants import LINKEDIN_DIR

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
USE_MAX_TIMER: bool = ast.literal_eval(config["USE_MAX_TIMER"])
JOB_MUST_CONTAIN: str = config["JOB_MUST_CONTAIN"]
STOP_AFTER_EVERY_JOB: bool = ast.literal_eval(config["STOP_AFTER_EVERY_JOB"])
PAUSE_AFTER_FAILURE: bool = ast.literal_eval(config["PAUSE_AFTER_FAILURE"])
PAUSE_AFTER_ANSWERING_QUESTIONS: bool = ast.literal_eval(config["PAUSE_AFTER_ANSWERING_QUESTIONS"])
START_AT_JOB_NUMBER_X: int = int(config["START_AT_JOB_NUMBER_X"])
GUESS_0_FOR_UNANSWERED: bool = ast.literal_eval(config["GUESS_0_FOR_UNANSWERED"])
BASE_URLS = ast.literal_eval(config["BASE_URLS"])
DO_NOT_APPLY_AT_THESE_COMPANIES = ast.literal_eval(
    config["DO_NOT_APPLY_AT_THESE_COMPANIES"])  # put in your current company
TEXT_DIR = config["TEXT_DIR"]
if not TEXT_DIR:
    TEXT_DIR = LINKEDIN_DIR + '/text/'
APPLIED_FOR_FILE = f'{TEXT_DIR}{config["APPLIED_FOR_FILE"]}'
ERROR_FILE = f'{TEXT_DIR}{config["ERROR_FILE"]}'
STATS_FILENAME = f'{TEXT_DIR}{config["STATS_FILENAME"]}'
JOB_NUMBER_FILENAME = f'{TEXT_DIR}{config["JOB_NUMBER_FILENAME"]}'
QUESTIONS_FILE = f'{TEXT_DIR}{config["QUESTIONS_FILE"]}'
UNANSWERED_QUESTIONS_FILE = f'{TEXT_DIR}{config["UNANSWERED_QUESTIONS_FILE"]}'
REFERENCES_FILE = f'{TEXT_DIR}{config["REFERENCES_FILE"]}'
SECONDS_TO_TRY_FOR = int(config["SECONDS_TO_TRY_FOR"])
