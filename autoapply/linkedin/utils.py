import os
import random
import time
from contextlib import suppress
from datetime import datetime, timedelta
from timeit import default_timer as timer

import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    InvalidElementStateException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from autoapply.linkedin.answers_broad import question_is_generic, question_mapper
from autoapply.linkedin.constants import QUESTION_FLUFF
from autoapply.linkedin.constants import QuestionType
from autoapply.linkedin.inputs import unanswered_question_file, PAUSE_AFTER_ANSWERING_QUESTIONS, PAUSE_AFTER_FAILURE, \
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


def get_questions_df(question_file, unanswered_question_file):
    df = pd.read_csv(question_file, delimiter=',', encoding='latin1')
    # Remove unanswered questions if any
    # Should only need done once, but was needed when the line of code did not exist
    df_answered = df[~df['answer'].isna()]
    df_unanswered = pd.read_csv(unanswered_question_file, delimiter=',', encoding='latin1')
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
    df4.to_csv(unanswered_question_file, sep=',', header=True, index=False, encoding='latin1')
    df5.to_csv(question_file, sep=',', header=True, index=False, encoding='latin1')
    df3 = df3.reset_index(drop=True)
    return df3


def is_radio_button_question(question):
    return len(question.find_elements('xpath', ".//input")) > 1


def answer_questions(dm, questions, tried_to_answer_questions, q_and_as_df, question_file, old_questions, url):
    if not tried_to_answer_questions:
        for question in questions:
            # if not question_is_required(question.text):
            #     continue
            # Drop down menu question/select
            # Issue if question is side by side
            logger.debug('\n' + question.text.replace("\n", " - "))
            logger.debug(f'{question.tag_name=}')
            q_m = QuestionManager(question)
            # having issue with this question
            # 'are legally allowed to work canadayesno'
            # 'Are you legally allowed to work in Canada\nRequired\nYes\nNo'
            question_text = question.text
            if q_m.question_type == QuestionType.radio:
                question_text = question_text.lower().split('required')[0].strip()
            q_text = clean_question_text(question_text)
            if q_m.question_type == QuestionType.dropdown:
                q_text = q_text.split('select an option')[0].strip()
            # question_type, q_text, text_options, select = get_question_type(question)
            question_type = q_m.question_type
            question_is_new = True
            q_text = remove_fluff_from_sentence(q_text)
            q_text = q_text.strip().replace('\n', '')
            q_text = q_text.replace(':', '').replace('"', "")
            q_text = q_text.encode('latin1', 'ignore').decode("latin1")
            logger.debug(question.text)
            question_mapped = question_mapper(question.text)
            if question_mapped != question.text:
                q_text = question_mapped
            generic_question, generic_answer = question_is_generic(question.text)
            if generic_answer != 'answer not found':
                q_m.answer_question(generic_answer)
                continue
            if 'by checking this box' in question.text.lower():
                options = question.find_elements('xpath', ".//label")
                options[0].click()  # Just check the box
                continue
            if q_text == 'city':
                put_answer_in_question_textbox('Montreal, Quebec, Canada', question)
                # For city question, need to click the box to continue
                with suppress():
                    dm.find_element('jobs-easy-apply-content').click()
                    time.sleep(0.5)
                continue
                # try:
                #     questions = WebDriverWait(question, 1).until(
                #         lambda question: question.find_elements('xpath', '//div[@role="listbox")]'))
                #     dropdown = WebDriverWait(question, 1).until(
                #         lambda question: question.find_element('xpath', "//ul"))
                #     # select first choice
                #     ActionChains(dm.driver).move_to_element(dropdown).click(button).perform()
                #     WebDriverWait(dropdown, 1).until(
                #         EC.element_to_be_clickable((By.XPATH, "//li"))).click()
                # except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                #     continue
            question_formatted = q_text.split(':')[0].replace('"', '')
            for index, row in q_and_as_df.iterrows():
                existing_question, existing_answer, times_asked = row[['question', 'answer', 'times_asked']]
                existing_question_formatted = str(existing_question).lower().split(':')[0].replace('"', '')
                if existing_question_formatted == question_formatted:
                    # Can switch to this now
                    logger.debug("q_and_as_df[q_and_as_df['question'] == question_formatted]")
                    logger.debug(q_and_as_df[q_and_as_df['question'] == question_formatted])
                    q_and_as_df.at[index, 'times_asked'] += 1
                    # https://www.linkedin.com/jobs/search/?currentJobId=3294737126&f_AL=true&f_E=2&f_JT=P%2CC%2CT%2CF&f_WT=1%2C2%2C3&geoId=101330853&keywords=it%20support&location=Montreal%2C%20Quebec%2C%20Canada&refresh=true&start=6
                    if (pd.isna(existing_answer)) or (existing_answer == ''):
                        logger.info(f'\tquestion found but no answer: "{existing_question}"')
                        break
                    answer = existing_answer.strip().lower()
                    # Answers are being recorded as floats, so convert to ints if we can
                    # Floats are not accepted
                    with suppress(ValueError):
                        answer = int(float(answer))
                    q_m.answer_question(answer)
                    # if question_type == QuestionType.text:
                    #     put_answer_in_question_textbox(answer, question)
                    # elif question_type == QuestionType.dropdown:
                    #     put_answer_in_question_dropdown(answer, text_options)
                    #     try:
                    #         index = text_options.index(answer)
                    #     except ValueError:  # ("if it's not found in the list")
                    #         continue
                    #     select.select_by_index(index)
                    # elif question_type == QuestionType.radio:
                    #     options = question.find_elements('xpath', ".//label")
                    #     answer_found = False
                    #     for option in options:
                    #         option_text = option.text.lower()
                    #         for fluff in QUESTION_FLUFF:
                    #             option_text = option_text.replace(fluff, '')
                    #         if ('oui' in option_text) or ('non' in option_text):
                    #             answer = translate_answer_to_french(answer)
                    #         if option.text.lower() == str(answer).lower():
                    #             answer_found = True
                    #             break
                    #     if not answer_found:
                    #         logger.info(f'\tdid not find answer for radio question {q_text}')
                    #     else:
                    #         option.click()
                    # else:
                    #     raise ValueError('question type unknown ' + question_type)
                    # # Unique case of textbox + dropdown
                    question_is_new = False
                    break
            if question_is_new:
                if (question_type == QuestionType.dropdown) or (question_type == QuestionType.radio):
                    if question_type == QuestionType.dropdown:
                        select = Select(question.find_elements('xpath', ".//select")[0])
                        text_options = [option.text.lower() for option in select.options]
                    elif question_type == QuestionType.radio:
                        options = question.find_elements('xpath', ".//label")
                        text_options = [option.text.lower() for option in options]
                    q_text = q_text + ':' + "^".join(text_options)
                else:
                    # if question_type == QuestionType.text:
                    try:
                        text_box = question.find_element('xpath', ".//input")
                    except NoSuchElementException:
                        text_box = question.find_element('xpath', ".//textarea")
                    with suppress(InvalidElementStateException):
                        text_box.clear()
                    # Uncomment to guess 0
                    # text_box.send_keys(0)
                try:
                    q_text2 = q_text.encode('latin1', 'ignore').decode("latin1").replace('"', '\"')
                    q_and_as_df = pd.concat([q_and_as_df, pd.DataFrame({'question': [q_text2]})])
                    logger.info(f'\tnew question: "{q_text2}"')
                    logger.info(f'\tnew question: "{question.text}"')
                except UnicodeEncodeError:
                    # Got error when question was in arabic
                    continue
        # Check that old_questions are not [], and questions don't match
        # We failed to answer questions if the page of questions is the same
        tried_to_answer_questions = old_questions and (questions == old_questions)
        if tried_to_answer_questions:
            old_questions = []
        else:
            old_questions = questions
    # update questions files
    q_and_as_df = q_and_as_df.sort_values('times_asked', ascending=False)
    df4 = q_and_as_df[q_and_as_df['answer'].isna()]
    df5 = q_and_as_df[~q_and_as_df['answer'].isna()]
    df4.to_csv(unanswered_question_file, sep=',', header=True, index=False, encoding='latin1')
    try:
        df5.to_csv(question_file, sep=',', header=True, index=False, encoding='latin1')
    except:
        time.sleep(1)
        df5.to_csv(question_file, sep=',', header=True, index=False, encoding='latin1')
    should_pause(PAUSE_AFTER_ANSWERING_QUESTIONS, "pause after answering questions")
    return tried_to_answer_questions, old_questions


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


def python_part_of_job(dm):
    job_title = dm.driver.find_element('xpath', "//h2[@class='t-24 t-bold jobs-unified-top-card__job-title']")
    if 'python' in job_title.text.lower():
        return True
    # check if job description has the word python in it
    job_details = dm.driver.find_element('xpath', "//div[@id='job-details']")
    if 'python' in job_details.text.lower():
        return True
    logger.info('skipping: python not in job title or description')
    return False


def click_sidebar_top_result(dm):
    # The sidebar often loads fast initially, then rerenders with additional choices
    # this causes the stale element exception, so just wait for 2 seconds
    # to avoid this situation
    time.sleep(2)
    try:
        sidebar = dm.find_element('scaffold-layout__list-container', 'ul', 'class', 3)
        # Find by attribute name
        lis = sidebar.find_elements('xpath', './/li[@data-occludable-job-id]')
        try:
            # Need to click title in this weird case
            title = lis[0].find_element('xpath', './/div[@id="ember369"]')
            title.click()
        except NoSuchElementException:
            lis[0].click()

        # for li in lis:
        #     if not 'promoted' in li.text.lower():
        #         li.click()
        #         break
    except (TimeoutException, StaleElementReferenceException) as e:
        logger.info(f'Unable to click sidebar, got a {e} error')


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


def get_questions_and_answers(question_file):
    # Also reorders questions file
    with open(question_file, 'r') as qf:
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

    df = pd.read_csv(question_file, delimiter=',', header=None, encoding='latin1')
    df3 = df.sort_values([1, 0], ascending=False)
    # df3.to_csv(question_file, sep=',', header=None, index=False)
    df3[0] = df3[0].str.lower()
    for fluff in QUESTION_FLUFF:
        df3[0] = df3[0].str.replace(fluff, '')
    df3[0] = df3[0].str.strip()
    df3 = df3.drop_duplicates(0)
    df3.to_csv(question_file, sep=',', header=None, index=False, encoding='latin1')
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


def put_answer_in_question_dropdown(answer, text_options, select):
    with suppress(ValueError):  # ("if it's not found in the list")
        index = text_options.index(answer)
        select.select_by_index(index)


class QuestionManager():
    def __init__(self, question_element: WebElement):
        self.element = question_element
        self.text = question_element.text.lower()
        self.question_type = get_question_type(question_element)

    def answer_question(self, answer):
        if self.question_type == QuestionType.text:
            put_answer_in_question_textbox(answer, self.element)
        elif self.question_type == QuestionType.dropdown:
            select = Select(self.element.find_elements('xpath', ".//select")[0])
            text_options = [option.text.lower() for option in select.options]
            put_answer_in_question_dropdown(answer, text_options, select)
            with suppress(ValueError):  # ("if it's not found in the list")
                index = text_options.index(answer)
                select.select_by_index(index)
        elif self.question_type == QuestionType.radio:
            options = self.element.find_elements('xpath', ".//label")
            answer_found = False
            for option in options:
                option_text = option.text.lower()
                for fluff in QUESTION_FLUFF:
                    option_text = option_text.replace(fluff, '')
                if ('oui' in option_text) or ('non' in option_text):
                    answer = translate_answer_to_french(answer)
                if option.text.lower() == str(answer).lower():
                    answer_found = True
                    break
            if not answer_found:
                logger.info(f'\tdid not find answer for radio question {self.text}')
            else:
                option.click()
        else:
            raise ValueError('question type unknown ' + self.question_type)


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
    def inner_func(job_title_el):
        job_title = job_title_el.text
        job_title = job_title.encode('latin1', 'ignore').decode("latin1")
        try:
            href = job_title_el.get_attribute('href')
            short_href = href.split('?')[0]
        except:
            logger.error("Unable to get href for current job. Not going to be able to save posting to applied_for.cv")
        return job_title, short_href

    try:
        # Element containing the href is an "a"
        job_title_el = dm.find_element(name="disabled ember-view job-card-container__link job-card-list__title",
                                       element="a")
        return inner_func(job_title_el)
    except TimeoutException:
        try:
            # Get job title from large description section and not sidebar if things fail
            h2_job_title_el = dm.find_element(name="t-24 t-bold job-details-jobs-unified-top-card__job-title",
                                              element="h2")
            h2_job_title_el_child = h2_job_title_el.find_element(by=By.XPATH, value='./*')
            return inner_func(h2_job_title_el_child)
        except TimeoutException:
            return '', ''


def have_applied_for_too_many_jobs_today():
    """
    Unclear if account will get flagged if we apply for too many jobs. After I think 100 jobs in the past 24 hours
    Linkedin will give an error saying "no results found" and you have to wait 24 hours to apply for more jobs
    To prevent account from being suspicous, stop applying for jobs after 90-95 jobs have been applied for
    """
    df = pd.read_csv(APPLIED_FOR_FILE, on_bad_lines="skip", encoding='latin1')
    df['date'] = pd.to_datetime(df['date'])
    mask = df['date'] > (datetime.now() - timedelta(hours=24))
    num_jobs_applied_for = mask.sum()
    logger.info(f"jobs applied for in past 24 hours {num_jobs_applied_for}")
    max_jobs = random.randint(90, 95)
    if num_jobs_applied_for > max_jobs:
        logger.info(f"applied for {num_jobs_applied_for} jobs in past 24 hours. Stopping")
        return True
    return False
