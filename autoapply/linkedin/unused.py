def get_last_job_applied_for_page_number(filename):
    with open(filename, 'r+') as jobf:
        job_number_str = jobf.read()
    if job_number_str == '':
        job_number = 0
    else:
        job_number = int(job_number_str)
    return job_number
