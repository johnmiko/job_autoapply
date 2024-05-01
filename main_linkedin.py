import json
import time
from datetime import datetime
from timeit import default_timer as timer

from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait

from autoapply.driver import driver_manager as DM
from autoapply.linkedin.answers import answer_questions
from autoapply.linkedin.constants import Page
from autoapply.linkedin.inputs import SECONDS_TO_TRY_FOR, JOB_NUMBER_FILENAME, STATS_FILENAME, \
    DO_NOT_APPLY_AT_THESE_COMPANIES, QUESTIONS_FILE, UNANSWERED_QUESTIONS_FILE, APPLIED_FOR_FILE, ERROR_FILE, \
    USE_MAX_TIMER, STOP_AFTER_EVERY_JOB
from autoapply.linkedin.utils import click_sidebar_top_result, get_questions_df, \
    keep_trying_to_submit_form, should_skip_company, should_pause, \
    write_to_file, get_pct_success_str, StatsManager, get_short_href_from_job_title, \
    have_applied_for_too_many_jobs_today, x_in_job_title_or_description, get_jobs_applied_for_in_past_24_hours
from autoapply.linkedin.utils import use_latest_resume
from autoapply.misc.utils import create_logger

logger, c_handler = create_logger(__name__)
logger.info('starting')
start = timer()
stats_manager = StatsManager(STATS_FILENAME)
df_stats = stats_manager.df
could_have_applied_for_cur_run = 0
applied_for_cur_run = 0
next_url = False
job_dict = {}
JOB_DETAILS = [{
    "url": "https://www.linkedin.com/jobs/search/?currentJobId=3905239413&distance=25&f_AL=true&f_WT=3%2C1%2C2&geoId=101330853&keywords=python%20developer&origin=JOBS_HOME_KEYWORD_HISTORY&refresh=true",
    "job_must_contain": ["python"]}, {
    "url": "https://www.linkedin.com/jobs/search/?currentJobId=3885951992&f_AL=true&f_WT=3%2C1%2C2&geoId=101330853&keywords=test%20automation%20engineer&location=Montreal%2C%20Quebec%2C%20Canada&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
    "job_must_contain": ["automation", "test", "qa"]}, {
    "url": "https://www.linkedin.com/jobs/search/?currentJobId=3881260700&f_AL=true&f_WT=2&geoId=101174742&keywords=python%20developer&location=Canada&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "job_must_contain": ["python"]}, {
    "url": "https://www.linkedin.com/jobs/search/?currentJobId=3914495894&f_AL=true&f_WT=2&geoId=101174742&keywords=test%20automation%20engineer&location=Canada&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "job_must_contain": ["automation", "test", "qa"]}, {
    "url": "https://www.linkedin.com/jobs/search/?currentJobId=3909150454&f_AL=true&f_WT=2&geoId=103644278&keywords=python%20developer&location=United%20States&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
    "job_must_contain": ["python"]}, {
    "url": "https://www.linkedin.com/jobs/search/?currentJobId=3909150454&f_AL=true&f_WT=2&geoId=103644278&keywords=test%20automation%20engineer&location=United%20States&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
    "job_must_contain": ["automation", "test", "qa"]}
]
job_details = JOB_DETAILS.copy()
# try:
#     with open(JOB_NUMBER_FILENAME, 'r+') as jobf:
#         job_number_dict = json.load(jobf)
#     if not job_number_dict:
#         job_number_dict = {}
# except FileNotFoundError:
#     job_number_dict = {}
# for job_detail in job_details:
#     job_detail["job_number"] = job_number_dict[job_detail["url"]]
try:
    job_number = -1
    job_number = 6
    while True:
        job_number += 1
        logger.info(f"{job_number=}")
        num_jobs_applied_for = get_jobs_applied_for_in_past_24_hours()
        logger.info(f"jobs applied for in past 24 hours {num_jobs_applied_for}")
        for job_detail in job_details:
            if have_applied_for_too_many_jobs_today():
                break
            if next_url:
                # coded but not really using
                # would depend on how we want to do things, apply for jobs in order? Or 1 to 1?
                job_number = 0
                next_url = False
                break
            want_to_apply_for_job = False
            url = f'{job_detail["url"]}&start={job_number}'
            DM.driver.get(url)
            no_jobs_found = DM.driver.find_elements('xpath', "//h1[text()='No matching jobs found.']")
            # job_dict[job_detail["url"]] += 1
            # logger.info(f'job number {job_dict[job_detail["url"]]}')
            try:
                click_sidebar_top_result(DM)
            except (TimeoutException, StaleElementReferenceException) as e:
                logger.info(f'Unable to click sidebar, got a {e} error')
                DM.driver.get(url)
            if 'https://www.linkedin.com/jobs/' not in DM.driver.current_url:
                logger.info('got redirected to a different site')
                continue

            page_not_loading_el = DM.driver.find_elements('xpath', "//h2[text()='Unfortunately, things aren’t "
                                                                   "loading']")
            # At page 48/49, constantly getting an error, not sure how to fix
            if page_not_loading_el:
                DM.driver.refresh()
                page_not_loading_el = DM.driver.find_elements('xpath', "//h2[text()='Unfortunately, things aren’t "
                                                                       "loading']")
                if page_not_loading_el:
                    logger.error(f"Page not loading twice in a row. On job number {job_number}")
                    break
            # Get job title and href to record to applied for
            job_title, short_href = get_short_href_from_job_title(DM)
            try:
                company_name = DM.driver.find_element('xpath', '//span[@class="job-card-container__primary-description '
                                                               '"]').text
            except NoSuchElementException:
                company_name = ''
            logger.info(f'\npost: {company_name}: {job_title}')
            if any(company.lower() in company_name.lower() for company in DO_NOT_APPLY_AT_THESE_COMPANIES):
                continue
            if job_detail["job_must_contain"] and (
                    not x_in_job_title_or_description(DM, job_detail["job_must_contain"], job_title)):
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
            q_and_as_df = get_questions_df(QUESTIONS_FILE, UNANSWERED_QUESTIONS_FILE)
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
                logger.debug(f'\ton page {h3s[0].text}')
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
                    tried_to_answer_questions, old_questions = answer_questions(DM, questions,
                                                                                tried_to_answer_questions,
                                                                                q_and_as_df, QUESTIONS_FILE,
                                                                                old_questions, url)
            now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            if submitted:
                write_to_file(APPLIED_FOR_FILE, 'a', 'date,company,position,url',
                              f'{now},"{company_name}","{job_title}","{short_href}"')
            if not submitted:
                write_to_file(ERROR_FILE, 'a', 'date,company,position,url,reason',
                              f'{now},{company_name},{job_title},{short_href},{reason}')
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
except Exception as e:
    logger.error(e)
    logger.error(url)
    raise e
finally:
    with open(JOB_NUMBER_FILENAME, 'w') as jobf:
        logger.info('writing job number to file')
        json.dump(job_dict, jobf)
    logger.info('finished')
breakpoint()
