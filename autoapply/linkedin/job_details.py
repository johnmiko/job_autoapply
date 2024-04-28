import json
from dataclasses import dataclass

from autoapply.linkedin.inputs import START_AT_JOB_NUMBER_X, JOB_NUMBER_FILENAME


@dataclass
class Details:
    url: str
    page_number: int
    notes: str


# Not being used now
def get_last_job_applied_for_page_number(url: str):
    if START_AT_JOB_NUMBER_X != -1:
        return START_AT_JOB_NUMBER_X
    try:
        with open(JOB_NUMBER_FILENAME, 'r+') as jobf:
            job_number_dict = json.load(jobf)
        if not job_number_dict:
            return 0
        return job_number_dict[url]
    except FileNotFoundError:
        return 0
