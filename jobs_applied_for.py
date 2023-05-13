import logging
import time
from timeit import default_timer as timer

from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
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
URL_BASE = 'https://www.linkedin.com/jobs/tracker/applied/'
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
