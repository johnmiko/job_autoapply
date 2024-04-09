from autoapply.constants import PROJ_DIR

POSTING = 'job_posting.txt'
COMPANY = 'Motion'
JOB_TITLE = 'QA Automation Engineer'
COVER_LETTER_TEXT_DIR = "D:/Users/johnm/OneDrive/ccode_files/job_autoapply/cover_letter/"
if not COVER_LETTER_TEXT_DIR:
    COVER_LETTER_TEXT_DIR = PROJ_DIR + 'text/'

# mechatronics engineer
# p1 = """As a developer with 8 years of programming experience, I find the responsibilities of this job posting straightforward and enjoyable.\n"""
PARAGRAPH_1 = """As a software developer with 10 years of experience, I believe I make an excellent candidate for 
this position.\n"""
OUTRO = f"""
Please take a moment to look over my resume and schedule a meeting with me (https://calendly.com/johnmiko/meeting) so we can further discuss my qualifications for the {JOB_TITLE} position. You can also reach me by email at johnmiko4@gmail.com. Thank you for taking the time to consider my application.

Sincerely,

John Miko
"""
