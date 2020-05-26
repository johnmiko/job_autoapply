import logging
import time
from timeit import default_timer as timer

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
logger.addHandler(c_handler)

from misc.kill_drivers import kill_drivers

kill_drivers('../misc/kill_drivers.bat')

# Initialize variables
# ----------INPUT VARIABLES---------- #
DEFAULT_LOAD_TIME = 5  # Time to wait for page/element to load before throwing error
# SHORT_LOAD_TIME = 30
URL_BASE = 'https://www.linkedin.com/jobs/search/?f_LF=f_AL'
# symbols_filename = 'symbols.txt'
all_filename = 'applied_for.csv'
error_file = 'errors.csv'

# ----------INPUT VARIABLES---------- #
logger.info('starting')
start = timer()
driver = webdriver.Edge()
wait = WebDriverWait(driver, DEFAULT_LOAD_TIME)  # create specific instance of webdriverwait with shorter timeout
try:
    driver.get(URL_BASE)
except NoSuchWindowException:
    time.sleep(0.5)
    driver.get(URL_BASE)
df = pd.DataFrame()
# old_company_name = WebDriverWait(driver, 10).until(
#     lambda driver: driver.find_element_by_xpath('//span[@class="companyInfCoName"]')).text
# list_len = len(symbols_list)
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
