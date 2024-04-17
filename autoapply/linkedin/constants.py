import logging
import os
from dataclasses import dataclass
from pathlib import Path

GLOBAL_LOG_LEVEL = logging.INFO
# GLOBAL_LOG_LEVEL = logging.DEBUG
LINKEDIN_DIR = os.path.dirname(os.path.abspath(Path(__file__)))
AUTOAPPLY_DIR = os.path.dirname(os.path.abspath(Path(__file__).parent))
PROJ_DIR = os.path.dirname(os.path.abspath(Path(__file__).parent.parent))
# LINKEDIN_DIR = f'{PROJ_DIR}/linkedin'
REMOTE = '&f_WRA=true'
CANADA = '&location=Canada'
ANYWHERE = '&geoId=92000000&location=Worldwide'
NORTH_AMERICA = '&geoId=102221843&location=North%20America'

QUESTION_FLUFF = ['please enter a valid answer', 'how many years', 'work experience', 'experience do you',
                  'what is your ', 'using ', 'with ', 'in ', 'do ', 'have ', 'you ', 'of ', 'as a ', 'currently have',
                  'depuis combien dannées utilisez-vous']


class Page:
    contact_info = 'Contact info'
    my_resume = 'John Miko - Resume.pdf'
    resume = 'Resume'
    CV = 'CV'
    additional_questions = 'Additional Questions'
    review_your_application = 'Review your application'


class QuestionType:
    dropdown = 'dropdown'
    radio = 'radio'
    text = 'text'



