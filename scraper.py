import logging
import time
from timeit import default_timer as timer

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, TimeoutException, ElementClickInterceptedException, \
    ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
logger.addHandler(c_handler)

from misc.kill_drivers import kill_drivers

kill_drivers('./misc/kill_drivers.bat')

# Initialize variables
# ----------INPUT VARIABLES---------- #
DEFAULT_LOAD_TIME = 5  # Time to wait for page/element to load before throwing error
SHORT_LOAD_TIME = 2
# all easy apply jobs
URL_BASE = 'https://www.linkedin.com/jobs/search/?f_LF=f_AL'
# all easy apply remote python jobs
URL_BASE = 'https://www.linkedin.com/jobs/search/?f_LF=f_AL&geoId=92000001&keywords=python&location=Remote'
# symbols_filename = 'symbols.txt'
all_filename = 'applied_for.csv'
error_file = 'errors.csv'

# ----------INPUT VARIABLES---------- #
logger.info('starting')
start = timer()
driver = webdriver.Edge()
wait = WebDriverWait(driver, DEFAULT_LOAD_TIME)  # create specific instance of webdriverwait with shorter timeout
short_wait = WebDriverWait(driver, SHORT_LOAD_TIME)
try:
    driver.get(URL_BASE)
except NoSuchWindowException:
    time.sleep(1.5)
    driver.get(URL_BASE)
df = pd.DataFrame()
# container = '//ul[@class="jobs-search-results__list artdeco-list"]'
# Only 7, going to need to scroll
postings_list = wait.until(lambda driver: driver.find_elements_by_xpath(
    '//li[@class="occludable-update artdeco-list__item--offset-2 artdeco-list__item p0 ember-view"]'))
list_len = len(postings_list)
postings_list = postings_list[:2]
c = 24
postings_list = wait.until(lambda driver: driver.find_elements_by_xpath(
    '//li[@class="occludable-update artdeco-list__item--offset-2 artdeco-list__item p0 ember-view"]'))

while True:
    # Applied 17 minutes ago span class partial text
    postings_list = wait.until(lambda driver: driver.find_elements_by_xpath(
        '//li[@class="occludable-update artdeco-list__item--offset-2 artdeco-list__item p0 ember-view"]'))
    try:
        postings_list[c].click()
    # If we've clicked all the buttons on the page
    except IndexError:
        # c == 25
        driver.get(f"https://www.linkedin.com/jobs/search/?f_LF=f_AL&start={c}")
    # If we already applied for for that job, continue
    c += 1
    try:
        short_wait.until(
            lambda driver: driver.find_element_by_xpath('//a[@data-control-name="jobs_tracker_link_applied"]'))
        continue
    except TimeoutException:
        pass
    time.sleep(1)
    try:
        # easy apply button
        wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="jobs-apply-button--top-card"]')).click()
    except TimeoutException:
        try:
            short_wait.until(
                lambda driver: driver.find_element_by_xpath('//div[@class="jobs-apply-button--top-card"]')).click()
        # Assume we already applied for the job so the button doesn't exist
        except TimeoutException:
            continue
    time.sleep(1)
    # Find next/review button
    # Need to loop until error
    submitted = False
    good_button_text = ['Next', 'Review', 'Submit application']
    loop_timer_start = timer()
    # end = timer()
    # elapsed = str(timer() - loop_timer_start)
    # Try doing this for 5 seconds
    while (not submitted) and ((timer() - loop_timer_start) < 5):
        try:
            buttons_list = wait.until(lambda driver: driver.find_elements_by_xpath(
                '//button[@class="artdeco-button artdeco-button--2 artdeco-button--primary ember-view"]'))
        except TimeoutException:
            # If something weird happens
            try:
                wait.until(
                    lambda driver: driver.find_element_by_xpath('//div[@class="jobs-apply-button--top-card"]')).click()
                buttons_list = wait.until(lambda driver: driver.find_elements_by_xpath(
                    '//button[@class="artdeco-button artdeco-button--2 artdeco-button--primary ember-view"]'))
            except ElementClickInterceptedException:
                break
        for button in buttons_list:
            if button.text in good_button_text:
                button.click()
                if 'Submit application' == button.text:
                    submitted = True
                break
        # # Try clicking yes radio button, if it doesn't exist continue
        # import pdb;
        #
        # pdb.set_trace()
        # try:
        #
        #     # choices = driver.find_elements_by_xpath("//div[contains(.,'5')][contains(@class, 'option')]
        #     #             driver.find_element_by_xpath('//input[contains(type="radio")][contains(@value,"Yes")]').click()
        #     #             ActionChains(driver).click(driver.find_element_by_xpath('//input[contains(@type,"radio")][contains(@value,"Yes")]')).perform()
        #     # Select(driver.find_element_by_xpath('//input[contains(@type,"radio")][contains(@value,"Yes")]')).perform()
        #     # radio-urn
        #     # driver.find_element_by_css_selector("input[type='radio'][value='Yes']").click()
        #     driver.find_element_by_css_selector("form").click()
        #     # driver.find_element_by('//input[contains(@type,"radio")][contains(@value,"Yes")]')).perform()
        # except InvalidSelectorException:
        #     pass
    # After submit, if there is a dismiss button, click it
    loop_timer_start = timer()
    done_dismissing = False
    while (not done_dismissing) and (timer() - loop_timer_start) < 5:
        # Click all the dismiss buttons
        try:
            short_wait.until(lambda driver: driver.find_element_by_xpath('//button[@aria-label="Dismiss"]')).click()
        except TimeoutException:
            done_dismissing = True
            break
        # If something weird happens
        except (ElementClickInterceptedException, ElementNotInteractableException):
            pass
        # If there is a discard application box afterwards
        try:
            short_wait.until(lambda driver: driver.find_element_by_xpath(
                '//button[@class="artdeco-modal__confirm-dialog-btn artdeco-button artdeco-button--2 artdeco-button--primary ember-view"]')).click()
            break
        except TimeoutException:
            pass

    #
    # except ElementClickInterceptedException:
    #     wait.until(lambda driver: driver.find_element_by_xpath('//button[@aria-label="Dismiss"]')).click()
    # try:
    #     wait.until(lambda driver: driver.find_element_by_xpath('//button[@aria-label="Dismiss"]')).click()
    # except (TimeoutException, ElementClickInterceptedException):
    #     pass
    # ("input[type='radio'][value='SRF']").click()

    # back review artdeco-button artdeco-button--2 artdeco-button--primary ember-view
    # back review

    # c = 0
    # for symbol in symbols_list:
    #     c += 1
    #     if c < SKIP_NUM:
    #         continue
    #     logger.info(f'symbol: {symbol}')
    #     logger.info(f'{c} of {list_len}')
    #     in_dict = {'timestamp': dt2.now(), 'symbol': symbol}
    #     time.sleep(2)
    #     symbols_input_box = wait.until(lambda driver: driver.find_element_by_class_name('symbolsInput'))
    #     symbols_input_box.clear()
    #     symbols_input_box.send_keys(symbol)
    #     symbols_input_box.send_keys(Keys.ENTER)
    #
    #     # Check that it actually changed the page
    #     company_name = wait.until(lambda driver: driver.find_element_by_xpath('//span[@class="companyInfCoName"]')).text
    #     # TODO: is a problem if it starts on Genmab
    #     while (old_company_name == company_name) and (company_name != 'Genmab A/S Ads'):
    #         company_name = wait.until(
    #             lambda driver: driver.find_element_by_xpath('//span[@class="companyInfCoName"]')).text
    #         time.sleep(0.5)
    #     old_company_name = company_name
    #     time.sleep(2)
    #     # +12% from Pivot in 6 days
    #     # -2% from Pivot in 5 days
    #     # 9% to Pivot
    #     try:
    #         pivot_and_days = wait.until(lambda driver: driver.find_element_by_xpath('//div[contains(text(), "Pivot")]'))
    #     except TimeoutException:
    #         symbols_input_box.send_keys(Keys.ENTER)
    #         time.sleep(1)
    #         try:
    #             pivot_and_days = wait.until(
    #                 lambda driver: driver.find_element_by_xpath('//div[contains(text(), "Pivot")]'))
    #         except TimeoutException:
    #             continue
    #     while pivot_and_days.text == '':
    #         pivot_and_days = wait.until(lambda driver: driver.find_element_by_xpath('//div[contains(text(), "Pivot")]'))
    #         time.sleep(0.5)
    #     try:
    #         percent_with_symbol, x_days = pivot_and_days.text.split(" from Pivot in ")
    #         # Remove percent symbol
    #         percent = float(percent_with_symbol[:-1]) * 0.01
    #         days, _ = x_days.split(" day")
    #     except ValueError:
    #         percent = int(pivot_and_days.text.split(" to Pivot")[0][:-1]) * -0.01
    #         days = None
    #     logger.debug(f'percent: {percent}')
    #     in_dict['pivot_percent_away'] = percent
    #     in_dict['days_since_pivot'] = days
    #     r_s_xpath = '//div[@class="label communityImg label_arrowHV"]'
    #     # Not sure what the 0'th element is
    #     right_sidebar = wait.until(lambda driver: driver.find_elements_by_xpath(r_s_xpath))
    #     # I can get the current price from IEX
    #     checklist_box = wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="checklistInner"]'))
    #     checklist_box.click()
    #     try:
    #         in_dict.update(add_checklist_to_dict(driver, wait, '//li[contains(text(), "William J. O\'Neil")]'))
    #     except StaleElementReferenceException:
    #         in_dict.update(add_checklist_to_dict(driver, wait, '//li[contains(text(), "William J. O\'Neil")]'))
    #     in_dict.update(add_checklist_to_dict(driver, wait, '//li[contains(text(), "Arnies Checklist")]'))
    #     df_single = pd.DataFrame([in_dict])
    #     df_single.to_csv(ALL_FILENAME, sep='_', mode='a', index=False, header=False)
    #     df = df.append(df_single, ignore_index=True)
    #
    # create_latest_csv(ALL_FILENAME, RECENT_FILENAME)
    #
    # end = timer()
    # elapsed = str(end - start)
    # logger.info(f'Run time in seconds: {elapsed}')
