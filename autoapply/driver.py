from enum import Enum

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_auto_update import check_driver

CHROMEDRIVER_PATH = 'C:/Users/johnm/OneDrive/miscellaneous/code/python/'
CHROMEDRIVER_EXE = f'{CHROMEDRIVER_PATH}chromedriver.exe'
CHROME_PROFILE = 'C:/Users/johnm/AppData/Local/Google/Chrome/User Data/profile1'

# To get partial matches use contains with xpath
# https://stackoverflow.com/questions/31248804/is-it-possible-to-locate-element-by-partial-id-match-in-selenium
# questions_radio = DM.driver.find_elements('xpath', '//div[contains(@class,"jobs-easy-apply-form-section__grouping")]')

SHORT_LOAD_TIME = 1
DEFAULT_LOAD_TIME = 5
check_driver(CHROMEDRIVER_PATH)
# https://stackoverflow.com/questions/66018451/how-to-get-the-chromedriver-automatically-updated-through-python-selenium-after
options = webdriver.ChromeOptions()
options.add_argument('user-data-dir=' + CHROME_PROFILE)  # Path to your chrome
chrome_driver = webdriver.Chrome(executable_path=CHROMEDRIVER_EXE, options=options)


class DriverManager(webdriver.Chrome):
    class ExBehaviour(Enum):
        default = 'default'  # does not use try/except
        none = 'none'  # passes

    def __init__(self, driver=None):
        if driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument('user-data-dir=' + CHROME_PROFILE)  # Path to your chrome
            self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_EXE, chrome_options=options)
        else:
            self.driver = driver

    # def open_first_url(self, url):
    #     # Edge can open the window too fast and crash itself, if it raises an error, try again in half a second
    #     try:
    #         self.driver.get(url)
    #     except NoSuchWindowException:
    #         time.sleep(0.5)
    #         self.driver.get(url)

    def xpath(self, element, prop, name):
        """
        Create xpath string given the element, element type/property, and the name of that property
        """
        # Don't include @ if text is used
        if prop == 'text()':
            # TODO: todo missing return statement here, seems to be okay though
            f'//{element}[{prop}="{name}"]'
        return f'//{element}[@{prop}="{name}"]'

    def find_element(self, name, element='div', prop='class', wait_time=SHORT_LOAD_TIME,
                     timeout_return_val=None, by='xpath'):
        if timeout_return_val is not None:
            try:
                return WebDriverWait(self.driver, wait_time).until(lambda driver: driver.find_element(by, self.xpath(
                    element, prop, name)))
            except TimeoutException:
                return timeout_return_val
        return WebDriverWait(self.driver, wait_time).until(lambda driver: driver.find_element(by, self.xpath(
            element, prop, name)))

    def find_elements(self, name, element='div', prop='class', wait_time=SHORT_LOAD_TIME,
                      timeout_return_val=None, by='xpath'):
        if timeout_return_val is not None:
            try:
                return WebDriverWait(self.driver, wait_time).until(lambda driver: driver.find_elements(by, self.xpath(
                    element, prop, name)))
            except TimeoutException:
                return timeout_return_val
        return WebDriverWait(self.driver, wait_time).until(lambda driver: driver.find_elements(by, self.xpath(
            element, prop, name)))


driver_manager = DriverManager(chrome_driver)
