import os
import random
import time
from contextlib import suppress
from datetime import datetime, timedelta
from timeit import default_timer as timer

import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from autoapply.linkedin.constants import QUESTION_FLUFF
from autoapply.linkedin.constants import QuestionType
from autoapply.linkedin.inputs import PAUSE_AFTER_FAILURE, \
    APPLIED_FOR_FILE
# https://stackoverflow.com/questions/38634988/check-if-program-runs-in-debug-mode
# def debugger_is_active():
#     gettrace = getattr(sys, 'gettrace')
#     if gettrace():
#         return True
#     return False
from autoapply.linkedin.wrappers import passTimeoutException
from autoapply.misc.utils import create_logger

logger, c_handler = create_logger(__name__)


def get_questions_df(QUESTIONS_FILE, UNANSWERED_QUESTIONS_FILE):
    df = pd.read_csv(QUESTIONS_FILE, delimiter=',', encoding='latin1')
    # Remove unanswered questions if any
    # Should only need done once, but was needed when the line of code did not exist
    df_answered = df[~df['answer'].isna()]
    df_unanswered = pd.read_csv(UNANSWERED_QUESTIONS_FILE, delimiter=',', encoding='latin1')
    df3 = pd.concat([df_answered, df_unanswered])
    df3['question'] = df3['question'].str.lower()
    for fluff in QUESTION_FLUFF:
        df3['question'] = df3['question'].str.replace(fluff, '')
    df3['question'] = df3['question'].str.strip()
    df3 = df3.drop_duplicates('question')
    df3['times_asked'] = df3['times_asked'].fillna(1)
    df3 = df3.sort_values('times_asked', ascending=False)
    df4 = df3[df3['answer'].isna()]
    df5 = df3[~df3['answer'].isna()]
    df4.to_csv(UNANSWERED_QUESTIONS_FILE, sep=',', header=True, index=False, encoding='latin1')
    df5.to_csv(QUESTIONS_FILE, sep=',', header=True, index=False, encoding='latin1')
    df3 = df3.reset_index(drop=True)
    return df3


def is_radio_button_question(question):
    return len(question.find_elements('xpath', ".//input")) > 1


def keep_trying_to_submit_form(tried_to_answer_questions, loop_timer_start, seconds_to_try_for,
                               USE_MAX_TIMER):
    cur_time = timer()
    max_seconds_occurred = ((cur_time - loop_timer_start) > seconds_to_try_for)
    logger.debug(f"{max_seconds_occurred=}")
    if max_seconds_occurred and USE_MAX_TIMER:
        try_to_submit_form = False
        reason = f"{seconds_to_try_for}s elapsed"
        logger.info(f'failure: {reason}')
    elif tried_to_answer_questions:
        try_to_submit_form = False
        reason = 'unable to answer questions'
        logger.info(f'failure: {reason}')
    else:
        try_to_submit_form = True
        reason = ''
    should_pause((not try_to_submit_form) and PAUSE_AFTER_FAILURE, context="pausing after failure")
    logger.debug(f'{try_to_submit_form=}')
    return try_to_submit_form, reason


@passTimeoutException
def should_skip_company(dm, list_of_companies_to_skip):
    company_name_raw = dm.find_element(name="ember-view t-black t-normal", element='a', prop='class').text
    company_name = company_name_raw.lower().replace(' ', '')
    for name in list_of_companies_to_skip:
        if name in company_name:
            logger.debug(f"skipping: don't want to apply at {company_name}")
            return True
    return False


def check_substring(string, substrings):
    for sub in substrings:
        if sub in string:
            return True
    return False


def x_in_job_title_or_description(dm, substrings: list, job_title: str):
    if any(sub in job_title.lower() for sub in substrings):
        return True
    job_details = dm.driver.find_element('xpath', "//div[@id='job-details']")
    if any(sub in job_details.text.lower() for sub in substrings):
        return True
    logger.info(f'skipping: {substrings} not in job title or description')
    return False


def click_sidebar_top_result(dm):
    # The sidebar often loads fast initially, then rerenders with additional choices
    # this causes the stale element exception, so just wait for 2 seconds
    # to avoid this situation
    time.sleep(2)
    sidebar = dm.find_element('scaffold-layout__list-container', 'ul', 'class', 3)
    # Find by attribute name
    lis = sidebar.find_elements('xpath', './/li[@data-occludable-job-id]')
    try:
        # Need to click title in this weird case
        title = lis[0].find_element('xpath', './/div[@id="ember369"]')
        title.click()
    except NoSuchElementException:
        lis[0].click()


def get_pct_success_str(jobs_applied_for, jobs_I_could_have_applied_for):
    try:
        return f"{jobs_applied_for} / {jobs_I_could_have_applied_for} - {int(jobs_applied_for / jobs_I_could_have_applied_for * 100)}%"
    except ValueError:
        # Catch error before first success
        return 0


class StatsManager:
    def __init__(self, filename):
        self.df = pd.read_csv(filename, index_col=0)
        self.df = self.df.fillna(0)
        self.could_have_applied_for_cur_run = 0
        self.applied_for_cur_run = 0

    def increment(self, columns, amount=1):
        if type(columns) == str:
            columns = [columns]
        for column in columns:
            self.df.loc[column, 'value'] = self.df.loc[column, 'value'] + amount
        if 'applied_for' in columns:
            logger.info('success: applied')

    def print_applied_for(self):
        logger.info(
            f"jobs applied for: {get_pct_success_str(self.df.loc['applied_for', 'value'], self.df.loc['could_have_applied_for', 'value'])}")


def should_pause(condition, context=""):
    if context:
        logger.debug(context)
    if condition:
        breakpoint()


def write_to_file(filename, mode, header, line):
    file_exists = os.path.isfile(filename)
    with suppress(UnicodeEncodeError):
        with open(filename, mode) as f:
            if not file_exists:
                f.write(f'{header}\n')
            f.write(f'{line}\n')


def get_questions_and_answers(QUESTIONS_FILE):
    # Also reorders questions file
    with open(QUESTIONS_FILE, 'r') as qf:
        lines = []
        for line in qf:
            if ',' not in line:
                line = line.strip('\n') + ',\n'
            # Missing answer
            # if line.endswith(':\n'):
            #     line = line[:-1] + '-1' + line[-1:]
            lines.append(line)
        # Remove duplicates if they exist and keep order
        lines = list(dict.fromkeys(lines))

    df = pd.read_csv(QUESTIONS_FILE, delimiter=',', header=None, encoding='latin1')
    df3 = df.sort_values([1, 0], ascending=False)
    # df3.to_csv(QUESTIONS_FILE, sep=',', header=None, index=False)
    df3[0] = df3[0].str.lower()
    for fluff in QUESTION_FLUFF:
        df3[0] = df3[0].str.replace(fluff, '')
    df3[0] = df3[0].str.strip()
    df3 = df3.drop_duplicates(0)
    df3.to_csv(QUESTIONS_FILE, sep=',', header=None, index=False, encoding='latin1')
    # df3.to_csv('temp.txt', sep=',', header=None, index=False)
    q_and_as = []
    for line in lines:
        q_and_as.append(line.strip('\n').split(','))

    return q_and_as


@passTimeoutException
def use_latest_resume(dm):
    choose_resume_els = dm.find_elements(name='Choose Resume', element='button', prop='aria-label', wait_time=2)
    latest_resume = choose_resume_els[0]
    latest_resume.click()


def question_is_required(question_text):
    text = question_text.lower()
    is_required = ('required' in text) or ('please enter a valid answer' in text)
    if is_required:
        logger.debug(f'question not mandatory - {text}')
    return is_required


def remove_fluff_from_sentence(text):
    for fluff in QUESTION_FLUFF:
        text = text.replace(fluff, '')
    text = text.strip().replace('\n', '')
    text = text.replace(':', '').replace('"', "")
    text = text.encode('latin1', 'ignore').decode("latin1")
    return text


def put_answer_in_question_textbox(answer, question: WebElement):
    try:
        text_box = question.find_element('xpath', ".//input")
    except NoSuchElementException:
        text_box = question.find_element('xpath', ".//textarea")
    text_box.clear()
    text_box.send_keys(str(answer))


def translate_answer_to_french(answer):
    answer_lower = str(answer).lower()
    if answer_lower == 'yes':
        return 'oui'
    elif answer_lower == 'no':
        return 'non'
    logger.info(f'needed to translate answer {answer} but was not able to')
    return answer_lower


def get_question_type(question_el):
    if question_el.find_elements('xpath', ".//select"):
        question_type = QuestionType.dropdown
    elif ('fieldset' == question_el.tag_name) or is_radio_button_question(question_el):
        question_type = QuestionType.radio
    else:
        # question.tag_name=='div'
        question_type = QuestionType.text
    return question_type


def clean_question_text(text):
    # Modifies the text here
    text = text.split('?')[0].lower().replace('\n', '').replace('required', '').strip()
    return text


def get_short_href_from_job_title(dm):
    def _inner_func(job_title_el):
        job_title = job_title_el.text.strip()
        job_title = job_title.encode('latin1', 'ignore').decode("latin1")
        try:
            href = job_title_el.get_attribute('href')
            short_href = href.split('?')[0]
        except:
            logger.error("Unable to get href for current job. Not going to be able to save posting to applied_for.cv")
        return job_title, short_href

    try:
        # Find first element where href has text /jobs/view
        # https://stackoverflow.com/questions/51370650/finding-an-element-by-partial-href-python-selenium
        job_title_el = dm.driver.find_element(by=By.XPATH, value="//a[contains(@href, '/jobs/view')]")
        return _inner_func(job_title_el)
    except TimeoutException:
        try:
            # Get job title from large description section and not sidebar if things fail
            h2_job_title_el = dm.find_element(name="t-24 t-bold job-details-jobs-unified-top-card__job-title",
                                              element="h2")
            h2_job_title_el_child = h2_job_title_el.find_element(by=By.XPATH, value='./*')
            return _inner_func(h2_job_title_el_child)
        except TimeoutException:
            logger.error("unable to find job title and posting link")
            return '', ''


def get_jobs_applied_for_in_past_24_hours():
    df = pd.read_csv(APPLIED_FOR_FILE, on_bad_lines="skip", encoding='latin1')
    df['date'] = pd.to_datetime(df['date'])
    mask = df['date'] > (datetime.now() - timedelta(hours=24))
    num_jobs_applied_for = mask.sum()
    return num_jobs_applied_for


def have_applied_for_too_many_jobs_today():
    """
    Unclear if account will get flagged if we apply for too many jobs. After I think 100 jobs in the past 24 hours
    Linkedin will give an error saying "no results found" and you have to wait 24 hours to apply for more jobs
    To prevent account from being suspicous, stop applying for jobs after 90-95 jobs have been applied for
    """
    num_jobs_applied_for = get_jobs_applied_for_in_past_24_hours()
    max_jobs = random.randint(70, 75)
    if num_jobs_applied_for > max_jobs:
        logger.info(f"applied for {num_jobs_applied_for} jobs in past 24 hours. Stopping")
        return True
    return False
