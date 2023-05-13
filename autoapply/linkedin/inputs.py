from autoapply.linkedin.constants import ANYWHERE, REMOTE, CANADA, NORTH_AMERICA, LINKEDIN_DIR

##### Settings - Frequent Changes - Start #####
# True, False
job_number = 0
# job_number = 15
USE_MAX_TIMER = True
# USE_MAX_TIMER = False
ONLY_PYTHON_JOBS = False
STOP_AFTER_EVERY_JOB = False
# STOP_AFTER_EVERY_JOB = True
PAUSE_AFTER_FAILURE = False
PAUSE_AFTER_ANSWERING_QUESTIONS = False
##### Settings - Frequent Changes - End #####
linkedin_url = 'https://www.linkedin.com/jobs/search/'
python_dev = '?f_AL=true&keywords=python%20developer'
global_warming_python = '?f_AL=true&keywords=global%20warming%20python'
clean_energy = '?f_AL=true&keywords=clean%20energy%20software'
# django_dev = '?f_AL=true&keywords=django%20developer'
# virtual_ass = '?f_AL=true&keywords=virtual%20assistant'
job_positions = [clean_energy, python_dev]
job_positions = [python_dev]
locations = [CANADA, ANYWHERE]
locations = [NORTH_AMERICA]
# full time and contract
job_type = '&f_JT=F%2CC'
renewable_energy_developer = 'https://www.linkedin.com/jobs/search/?currentJobId=3252800002&f_AL=true&f_I=144&f_WT=2&geoId=92000000&keywords=developer&location=Worldwide&refresh=true&sortBy=R'
base_urls = [renewable_energy_developer]
base_urls = []
for position in job_positions:
    for location in locations:
        base_urls.append(linkedin_url + position + REMOTE + location + job_type)
# on site remote python developer jobs montreal
base_urls = [
    'https://www.linkedin.com/jobs/search/?currentJobId=3348387602&f_AL=true&f_JT=F%2CC&f_WT=1%2C2%2C3&geoId=101330853&keywords=python%20developer&location=Montreal%2C%20Quebec%2C%20Canada&refresh=true']
# python developer jobs canada
base_urls = [
    'https://www.linkedin.com/jobs/search/?currentJobId=3348073574&f_AL=true&f_JT=F%2CC&f_WT=2&keywords=python%20developer&refresh=true']
# python developer jobs north america
base_urls = [
    'https://www.linkedin.com/jobs/search/?currentJobId=3356498079&f_AL=true&f_JT=F%2CC&f_WT=2&geoId=102221843&keywords=python%20developer&location=North%20America&refresh=true']
# remote administrative assistant, entry level
base_urls = [
    'https://www.linkedin.com/jobs/search/?currentJobId=3081574561&f_AL=true&f_E=2&f_JT=F%2CP%2CC%2CT&f_WT=2&geoId=102221843&keywords=administrative%20assistant&location=North%20America&refresh=true']
# it support, montreal, entry level, remote, hybrid, have to go in
base_urls = [
    'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2&f_JT=P%2CC%2CT%2CF&f_WT=1%2C2%2C3&geoId=101330853&keywords=it%20support&location=Montreal%2C%20Quebec%2C%20Canada&refresh=true']
TEXT_DIR = LINKEDIN_DIR + '/text/'
APPLIED_FOR_FILE = f'{TEXT_DIR}applied_for.csv'
ERROR_FILE = f'{TEXT_DIR}errors.txt'
question_file = f'{TEXT_DIR}questions.txt'
unanswered_question_file = f'{TEXT_DIR}unanswered_questions.txt'
SECONDS_TO_TRY_FOR = 90
