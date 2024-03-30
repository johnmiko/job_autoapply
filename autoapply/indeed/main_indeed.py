import time
from contextlib import suppress
from datetime import datetime
from timeit import default_timer as timer

from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from autoapply.driver import driver_manager as DM
from autoapply.indeed.constants import JOB_NUMBER_FILENAME, INDEED_DIR, Page, STATS_FILENAME
from autoapply.linkedin.inputs import ONLY_PYTHON_JOBS, question_file, unanswered_question_file, USE_MAX_TIMER, \
    APPLIED_FOR_FILE, ERROR_FILE, STOP_AFTER_EVERY_JOB
from autoapply.linkedin.utils import python_part_of_job, click_sidebar_top_result, get_questions_df, \
    keep_trying_to_submit_form, answer_questions, should_skip_company, should_pause, \
    write_to_file, get_pct_success_str, StatsManager, QuestionManager
from autoapply.misc.utils import create_logger

logger, c_handler = create_logger(__name__)
# from misc.kill_drivers import kill_drivers
#
# kill_drivers(PROJ_DIR + '/misc/kill_drivers.bat')

logger.info('starting')
# page 2
base_urls = [
    'https://ca.indeed.com/jobs?q=IT+%2440%2C000&sc=0kf%3Aattr%28DSQF7%29%3B&lang=en&start=10&pp=gQAPAAAAAAAAAAAAAAAB8wlwqwAtAQACw_hhcfW9JhUr1lcpAMKf_iWm-ImmcHEvwaQKiYKaoIz9a9xLvmEfYil2AAA&vjk=720ae99d5640aa08&advn=4672087812901408']
# page 1
base_urls = [
    'https://ca.indeed.com/jobs?q=IT+%2440%2C000&sc=0kf%3Aattr%28DSQF7%29%3B&lang=en&pp=gQAAAAAAAAAAAAAAAAAB8wlwqwADAAABAAA&vjk=492a502e45e2c95a']
start = timer()
# job_number = get_last_job_applied_for_page_number(JOB_NUMBER_FILENAME)
job_number = 0
stats_manager = StatsManager(STATS_FILENAME)
df_stats = stats_manager.df
# initialize variables
seconds_to_try_for = 30
could_have_applied_for_cur_run = 0
applied_for_cur_run = 0

next_url = False
reset_job_number = False

with open(INDEED_DIR + '/text/completed.txt', 'r') as f:
    urls_complete = [line.strip('\n') for line in f]
try:
    for base_url in base_urls:
        if base_url in urls_complete:
            continue
        while True:
            if next_url:
                reset_job_number = True
                next_url = False
                break
            if reset_job_number:
                job_number = 0
            want_to_apply_for_job = False
            logger.info(f'\npost: {job_number} ')
            url = f'{base_url}&start={job_number}'
            DM.driver.get(url)
            # If popup, need to close it
            with suppress(TimeoutException):
                # DM.find_element('xpath', "div", "aria-labelledby", "modal-mosaic-desktopserpjapopup", 0.5)
                # TODO: check if we can just click the close button, no need to check for thexistance of both It hink
                DM.find_element(name="close", element="button", prop='aria-label', wait_time=0.5).click()
            # Find list of jobs
            #
            # job_cards_all = DM.find_element('xpath', "div", 'id', "mosaic-jobcards", 0.5)
            # job_cards = job_cards_all.find_elements('xpath', ".//li")
            # may want to use this too, it's stored in a ul, and each is a li
            job_cards_all = DM.find_element("jobsearch-ResultsList css-0", "ul", 'class', 0.5)
            job_cards = DM.find_elements("slider_container css-g7s71f eu4oa1w0", wait_time=0.5)
            for job_card in job_cards:
                job_card.click()
                job_properties = DM.find_element("jobsearch-ViewjobPaneWrapper", 'div', 'id', 1)
                qualifications = DM.find_element("qualificationsSection", "div", 'id', 0.5, [])
                job_description = DM.find_element("jobDescriptionText", "div", 'id', 0.5)
                # Lot of stuff here, not sure what I need exactly

                job_details_section = DM.find_element("jobDetailsSection", "div", 'id', 0.5)
                # Think I need to click somewhere to make the button interactable
                job_details_section.click()
                try:
                    # if easy apply button doesn't exist
                    # Actual button says it's not interactable?
                    # apply_button =
                    # Click inner button
                    # button = DM.find_element(" css-zv0ejl e8ju0x51", "button", 'class', 0.5)
                    # DM.find_element(" css-zv0ejl e8ju0x51", "button", 'class', 0.5).click()
                    # DM.find_element("indeedApplyButton", "button", 'id', 0.5).click()
                    button = DM.find_element("ia-IndeedApplyButton", "div", 'class', 0.5)
                    # https://stackoverflow.com/questions/44119081/how-do-you-fix-the-element-not-interactable-exception
                    ActionChains(DM.driver).move_to_element(button).click(button).perform()
                except TimeoutException:
                    continue
                # page changes, check url I guess?
                # need to get list of questions and answer them
                DM.driver.switch_to.window(DM.driver.window_handles[1])
                # check that we're on the correct url
                if DM.driver.current_url == 'https://m5.apply.indeed.com/beta/indeedapply/form/questions/1':
                    print('not on correct url yet')
                logger.info(f'url: {DM.driver.current_url}')
                # try clicking continue button
                continue_button = DM.find_element('ia-continueButton ia-Resume-continue css-vw73h2 e8ju0x51', "button")
                continue_button.click()
                questions = WebDriverWait(DM.driver, 1).until(lambda driver: driver.find_elements('xpath',
                                                                                                  '//div[contains(@class,"ia-Questions-item")]'))
                # questions_all = DM.find_element("ia-BasePage ia-Questions", "div", 'class', 0.5, timeout_return_val=[])
                for question in questions:
                    question_text = question.text.lower()
                    if question_text == 'please list 2-3 dates and time ranges that you could do an interview.(optional)':
                        q_m = QuestionManager(question)
                        # Need to record the questions and answer them
                        q_m.answer_question('https://calendly.com/johnmiko/meeting')
                q_and_answer_els = WebDriverWait(DM.driver, 0.5).until(
                    lambda driver: driver.find_elements("//*[contains(@id, 'q_')]"))
                # q_and_answer_els = DM.find_element("div", 'class', "ia-BasePage ia-Questions", 0.5)
                # driver.find_elements_by_xpath('//*[contains(@id, 'cell.line.order(240686080)')]')
                a = DM.find_element("div", 'id', "a", 0.5)
                a = DM.find_element("div", 'id', "a", 0.5)
                a = DM.find_element("div", 'id', "a", 0.5)
                a = DM.find_element("div", 'id', "a", 0.5)
                a = DM.find_element("div", 'id', "a", 0.5)

            # class="jobsearch-ResultsList css-0" <- ul
            #
            popup = DM.driver.find_elements("//h1[text()='No matching jobs found.']")
            no_jobs_found = DM.driver.find_elements("//h1[text()='No matching jobs found.']")
            job_number += 1
            # job_title_el = DM.find_element('xpath',
            #     "//h2[@class='t-24 t-bold jobs-unified-top-card__job-title']")
            job_title_el = DM.find_element("h2", "class", "t-24 t-bold jobs-unified-top-card__job-title", 4)
            job_title = job_title_el.text
            job_title = job_title.encode('latin1', 'ignore').decode("latin1")
            href = job_title_el.find_element('xpath', '..').get_attribute('href')
            short_href = href.split('?')[0]
            click_sidebar_top_result(DM)
            # get_posting_url()
            if 'www.linkedin.com' not in DM.driver.current_url:
                logger.info('got redirected to a different site')
                continue
            try:
                company_name = DM.driver.find_element('xpath', '//a[@class="ember-view t-black t-normal"]').text
            except NoSuchElementException:
                company_name = ''
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
                    # TODO: todo missing return statement here, seems to be okay though
                    # In the xpath part where we check if the value is text...
                    no_more_results = DM.find_elements('xpath', 'h2', 'text()', 'Unfortunately, things aren’t loading',
                                                       1)
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
            # driver.find_element('xpath',self.xpath(element, prop, name)))
            # with ignoring(NoSuchElementException, action=log):
            #     something()
            with suppress(NoSuchElementException):
                # Check if "Applied X time ago" element exists, if so, we already applied
                stats_manager.increment('already_applied')
                DM.driver.find_element('xpath', DM.xpath('span', 'class', 'artdeco-inline-feedback__message'))
                logger.info('skipping: already applied')
                continue
            try:
                DM.find_element('xpath', 'div', 'class', 'jobs-apply-button--top-card', 1).click()
                easy_apply_button = None
            except TimeoutException:
                # Path taken when job already applied for
                logger.info('skipping: already applied')
                continue
            # Not sure why this occurs, think it is referring to the old dom, if so, try again
            except (StaleElementReferenceException, ElementNotInteractableException):
                try:
                    DM.find_element('xpath', 'div', 'class', 'jobs-apply-button--top-card', 1).click()
                except (StaleElementReferenceException, ElementNotInteractableException):
                    # Was unable to click the easy apply button for some reason, just skip job for now
                    # Can also occur if it says "no longer accepting applications" and there is no button
                    logger.info('had StaleElementReferenceException, skipping job')
                    stats_manager.increment('skipped')
                    logger.info(f"jobs skipped {stats_manager.df.loc['skipped', 'value']}")
                    submitted = True
            time.sleep(1)
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
            logger.debug(f"{seconds_to_try_for=}")
            try_to_submit_form, reason = keep_trying_to_submit_form(tried_to_answer_questions, loop_timer_start,
                                                                    seconds_to_try_for,
                                                                    USE_MAX_TIMER)
            while try_to_submit_form:
                try_to_submit_form, reason = keep_trying_to_submit_form(tried_to_answer_questions, loop_timer_start,
                                                                        seconds_to_try_for, USE_MAX_TIMER)
                if not try_to_submit_form:
                    stats_manager.increment(['could_have_applied_for', 'failures'])
                    could_have_applied_for_cur_run += 1
                    logger.info(
                        f"current run: {get_pct_success_str(applied_for_cur_run, could_have_applied_for_cur_run)}")
                    stats_manager.print_applied_for()
                    break
                h3s = DM.driver.find_elements('xpath', "//h3")
                pages_to_skip = [Page.review_your_application, Page.my_resume, Page.contact_info]
                need_to_answer_questions = True
                for h3 in h3s:
                    if h3.text in pages_to_skip:
                        logger.debug(f'{h3.text=}, skipping page')
                        need_to_answer_questions = False
                    elif h3.text == Page.resume:
                        use_latest_resume(DM)
                if need_to_answer_questions:
                    try:
                        questions_dropdowns_and_text = DM.find_elements('xpath', 'div',
                                                                        'class',
                                                                        'fb-form-element mt4 jobs-easy-apply-form-element',
                                                                        5)
                    except TimeoutException:
                        # if there is only radio buttons
                        questions_dropdowns_and_text = []
                    try:
                        questions_radio = DM.find_elements('xpath', 'fieldset', 'class',
                                                           'fb-form-element mt4 jobs-easy-apply-form-element',
                                                           3)
                    except:
                        questions_radio = []
                    questions = questions_dropdowns_and_text + questions_radio
                    # try to scroll to bottom of page
                    with suppress():
                        popup = DM.find_element('xpath', 'div', 'class',
                                                'artdeco-modal__content jobs-easy-apply-modal__content p0 ember-view',
                                                2)
                        DM.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", popup)
                    #
                    tried_to_answer_questions, old_questions = answer_questions(questions, tried_to_answer_questions,
                                                                                q_and_as_df, question_file,
                                                                                old_questions)
                try:
                    buttons_list = DM.find_elements('xpath', 'button', 'class',
                                                    'artdeco-button artdeco-button--2 artdeco-button--primary ember-view',
                                                    1)
                except TimeoutException:
                    # If something weird happens
                    try:
                        DM.find_element('xpath', 'div', 'class', 'jobs-apply-button--top-card', 1).click()
                        buttons_list = DM.find_elements('xpath', 'button', 'class',
                                                        'artdeco-button artdeco-button--2 artdeco-button--primary ember-view',
                                                        1)
                    except (ElementClickInterceptedException, TimeoutException):
                        logger.debug(f"wasn't able to find the list of buttons to go to next page")
                        continue
                for button in buttons_list:
                    if button.text in valid_button_text:
                        with suppress():
                            button.click()
                        # Could reorder this I think.
                        with suppress(StaleElementReferenceException):
                            if 'Submit application' == button.text:
                                submitted = True
                                stats_manager.increment(['applied_for', 'could_have_applied_for'])
                                applied_for_cur_run += 1
                                could_have_applied_for_cur_run += 1
                                logger.info(
                                    f"current run: {get_pct_success_str(applied_for_cur_run, could_have_applied_for_cur_run)}")
                                stats_manager.print_applied_for()
                                break
                        break
                if submitted:
                    today = datetime.today().strftime("%Y-%m-%d")
                    write_to_file(APPLIED_FOR_FILE, 'a', 'date,company,position,url',
                                  f'{today},{company_name},{job_title},{short_href}')
                    break
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
            time.sleep(2)
            should_pause(STOP_AFTER_EVERY_JOB)
finally:
    with open(JOB_NUMBER_FILENAME, 'w') as jobf:
        logger.info('writing job number to file')
        jobf.write(str(job_number))
logger.info('finished')
