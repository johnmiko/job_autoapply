import time
from datetime import datetime
from timeit import default_timer as timer

from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait

from autoapply.driver import driver_manager as DM
from autoapply.linkedin.constants import JOB_NUMBER_FILENAME, Page, STATS_FILENAME, LINKEDIN_DIR
from autoapply.linkedin.inputs import SECONDS_TO_TRY_FOR
from autoapply.linkedin.inputs import (base_urls, ONLY_PYTHON_JOBS, question_file, unanswered_question_file,
                                       USE_MAX_TIMER, \
                                       APPLIED_FOR_FILE, ERROR_FILE, STOP_AFTER_EVERY_JOB)
from autoapply.linkedin.unused import get_last_job_applied_for_page_number
from autoapply.linkedin.utils import create_logger, python_part_of_job, click_sidebar_top_result, get_questions_df, \
    keep_trying_to_submit_form, answer_questions, should_skip_company, should_pause, \
    write_to_file, get_pct_success_str, StatsManager, get_short_href_from_job_title
from autoapply.linkedin.utils import use_latest_resume

logger, c_handler = create_logger(__name__)
logger.info('starting')
start = timer()
job_number = get_last_job_applied_for_page_number(JOB_NUMBER_FILENAME)
# job_number = 0
stats_manager = StatsManager(STATS_FILENAME)
df_stats = stats_manager.df
# initialize variables
could_have_applied_for_cur_run = 0
applied_for_cur_run = 0
next_url = False

with open(LINKEDIN_DIR + '/text/completed.txt', 'r') as f:
    urls_complete = [line.strip('\n') for line in f]
try:
    for base_url in base_urls:
        if base_url in urls_complete:
            continue
        while True:
            if next_url:
                job_number = 0
                next_url = False
                break
            want_to_apply_for_job = False
            url = f'{base_url}&start={job_number}'
            DM.driver.get(url)
            no_jobs_found = DM.driver.find_elements('xpath', "//h1[text()='No matching jobs found.']")
            job_number += 1
            click_sidebar_top_result(DM)
            if 'https://www.linkedin.com/jobs/search/' not in DM.driver.current_url:
                logger.info('got redirected to a different site')
                continue
            # TODO: company and job title not working anymore
            job_title, short_href = get_short_href_from_job_title(DM)
            try:
                company_name = DM.driver.find_element('xpath', '//span[@class="job-card-container__primary-description '
                                                               '"]').text
                #
            except NoSuchElementException:
                company_name = ''
            logger.info(f'\npost: {job_number} - {company_name}: {job_title}')
            if ONLY_PYTHON_JOBS and (not python_part_of_job(DM)):
                stats_manager.increment('skipped')
                time.sleep(3)
                continue
            if no_jobs_found:
                logger.info('no jobs found, going to next url')
                next_url = True
                continue
            no_more_results = False
            max_attempts = 10
            attempt = 0
            while True:
                try:
                    no_more_results = DM.find_elements(name='Unfortunately, things aren’t loading', element='h2',
                                                       prop='text()')
                except TimeoutException:
                    break
                DM.driver.get(url)
                # Sometimes the page just doesn't load
                # Try 10 times before giving
                attempt += 1
                logger.debug(f"page didn't load, trying again, attempt={attempt}/{max_attempts}")
                if attempt > max_attempts:
                    logger.info(f"no more results for {url}\n after {job_number} jobs")
                    next_url = True
                    break
            if next_url:
                breakpoint()
                continue
            should_skip_company(DM, [])
            submitted = False
            try:
                # Check if "Applied X time ago" element exists, if so, we already applied
                stats_manager.increment('already_applied')
                DM.driver.find_element('xpath', DM.xpath('span', 'class', 'artdeco-inline-feedback__message'))
                logger.info(f'\tskipping: already applied at {company_name} - {job_title}')
                continue
            except NoSuchElementException:
                pass
            try:
                DM.find_element('jobs-apply-button--top-card').click()
                easy_apply_button = None
            except TimeoutException:
                # Path taken when job already applied for
                logger.info('\tskipping: already applied')
                continue
            # Not sure why this occurs, think it is referring to the old dom, if so, try again
            except (StaleElementReferenceException, ElementNotInteractableException):
                try:
                    DM.find_element('jobs-apply-button--top-card').click()
                except (StaleElementReferenceException, ElementNotInteractableException):
                    # Was unable to click the easy apply button for some reason, just skip job for now
                    # Can also occur if it says "no longer accepting applications" and there is no button
                    logger.info('\thad StaleElementReferenceException, skipping job')
                    stats_manager.increment('skipped')
                    logger.info(f"jobs skipped {stats_manager.df.loc['skipped', 'value']}")
                    submitted = True
            # time.sleep(1)
            # Find next/review button
            # Need to loop until error
            q_and_as_df = get_questions_df(question_file, unanswered_question_file)
            valid_button_text = ['Next', 'Review', 'Submit application']
            loop_timer_start = timer()
            tried_to_answer_questions = False
            old_questions = []
            logger.debug(f"{tried_to_answer_questions=}")
            logger.debug(f"{submitted=}")
            logger.debug(f"{loop_timer_start=}")
            logger.debug(f"{ SECONDS_TO_TRY_FOR=}")
            try_to_submit_form, reason = keep_trying_to_submit_form(tried_to_answer_questions, loop_timer_start,
                                                                    SECONDS_TO_TRY_FOR,
                                                                    USE_MAX_TIMER)
            while try_to_submit_form:
                # Just try twice, otherwise continue
                # for i in range(0,2):
                try_to_submit_form, reason = keep_trying_to_submit_form(tried_to_answer_questions, loop_timer_start,
                                                                        SECONDS_TO_TRY_FOR, USE_MAX_TIMER)
                if not try_to_submit_form:
                    stats_manager.increment(['could_have_applied_for', 'failures'])
                    could_have_applied_for_cur_run += 1
                    logger.info(
                        f"current run: {get_pct_success_str(applied_for_cur_run, could_have_applied_for_cur_run)}")
                    stats_manager.print_applied_for()
                    break
                try:
                    buttons_list = DM.find_elements(
                        name='artdeco-button artdeco-button--2 artdeco-button--primary ember-view', element='button',
                        prop='class')
                except TimeoutException:
                    # If something weird happens
                    try:
                        DM.find_element('jobs-apply-button--top-card').click()
                        buttons_list = DM.find_elements(
                            name='artdeco-button artdeco-button--2 artdeco-button--primary ember-view',
                            element='button', prop='class')
                    except (ElementClickInterceptedException, TimeoutException):
                        logger.debug(f"wasn't able to find the list of buttons to go to next page")
                        continue
                h3s = DM.driver.find_elements('xpath', "//h3")
                pages_to_skip = [Page.review_your_application, Page.my_resume, Page.contact_info]
                need_to_answer_questions = True
                for h3 in h3s:
                    try:
                        if h3.text in pages_to_skip:
                            logger.debug(f'{h3.text=}, skipping page')
                            need_to_answer_questions = False
                        elif (h3.text == Page.resume) or (h3.text == Page.CV):
                            use_latest_resume(DM)
                            logger.debug(f'{h3.text=}, skipping page')
                    except StaleElementReferenceException:
                        pass
                logger.info(f'\ton page {h3s[0].text}')
                if h3s[0].text == 'Home address':
                    a = 1
                for button in buttons_list:
                    if button.text in valid_button_text:
                        try:
                            button.click()
                        except:
                            try:
                                DM.find_element('jobs-easy-apply-content').click()
                                time.sleep(0.5)
                                button.click()
                            except:
                                pass
                        try:
                            if 'Submit application' == button.text:
                                submitted = True
                                stats_manager.increment(['applied_for', 'could_have_applied_for'])
                                applied_for_cur_run += 1
                                could_have_applied_for_cur_run += 1
                                logger.info(
                                    f"current run: {get_pct_success_str(applied_for_cur_run, could_have_applied_for_cur_run)}")
                                stats_manager.print_applied_for()
                                try_to_submit_form = False
                                break
                        except StaleElementReferenceException:
                            pass
                        break
                try:
                    questions = WebDriverWait(DM.driver, 1).until(lambda driver: driver.find_elements('xpath',
                                                                                                      '//div[contains(@class,"jobs-easy-apply-form-section__grouping")]'))
                except TimeoutException:
                    questions = []
                # try to scroll to bottom of page
                try:
                    popup = DM.find_element('artdeco-modal__content jobs-easy-apply-modal__content p0 ember-view')
                    DM.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", popup);
                except:
                    pass
                if try_to_submit_form:
                    # TODO: create some
                    tried_to_answer_questions, old_questions = answer_questions(DM, questions,
                                                                                tried_to_answer_questions,
                                                                                q_and_as_df, question_file,
                                                                                old_questions, url)
            if submitted:
                today = datetime.today().strftime("%Y-%m-%d")
                write_to_file(APPLIED_FOR_FILE, 'a', 'date,company,position,url',
                              f'{today},{company_name},{job_title},{short_href}')
        if not submitted:
            today = datetime.today().strftime("%Y-%m-%d")
            write_to_file(ERROR_FILE, 'a', 'date,company,position,url,reason',
                          f'{today},{company_name},{job_title},{short_href},{reason}')
        elapsed = int(timer() - start)
        start = timer()
        stats_manager.increment('running_time (s)', elapsed)
        stats_manager.df.loc['running_time (m)', 'value'] = int(
            stats_manager.df.loc['running_time (s)', 'value'] / 60)
        stats_manager.df.loc['jobs / min', 'value'] = stats_manager.df.loc['applied_for', 'value'] / \
                                                      stats_manager.df.loc[
                                                          'running_time (m)', 'value']
        stats_manager.df.loc['success rate', 'value'] = int(
            stats_manager.df.loc['applied_for', 'value'] / stats_manager.df.loc[
                'could_have_applied_for', 'value'] * 100)
        stats_manager.df.to_csv(STATS_FILENAME, index=True, header=True)
        should_pause(STOP_AFTER_EVERY_JOB)
finally:
    with open(JOB_NUMBER_FILENAME, 'w') as jobf:
        logger.info('writing job number to file')
        jobf.write(str(job_number))
    logger.info('finished')
