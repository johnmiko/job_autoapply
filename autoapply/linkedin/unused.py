from autoapply.linkedin.inputs import START_AT_JOB_NUMBER_X, JOB_NUMBER_FILENAME


def get_last_job_applied_for_page_number():
    if START_AT_JOB_NUMBER_X != -1:
        return START_AT_JOB_NUMBER_X
    with open(JOB_NUMBER_FILENAME, 'r+') as jobf:
        job_number_str = jobf.read()
    if job_number_str == '':
        job_number = 0
    else:
        job_number = int(job_number_str)
    return job_number
