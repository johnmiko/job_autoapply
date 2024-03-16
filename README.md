# linkedin_autoapply

## Installation

pip install -r requirements.txt

In the file autoapply/linkedin/inputs.py, paste in the url or urls, that you want to apply for. Example I want to
apply for test automation jobs in the United States that are remote. So I paste in

```
"https://www.linkedin.com/jobs/search/?currentJobId=3840550772&f_AL=true&f_WT=2&geoId=103644278&keywords=test%20automation&location=United%20States&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
```

Currently variables are set to just "run". But you can enter debugging mode after answering a page of questions or
submitting an application if you want to inspect what the code is actually doing.
Max timer is used to handle edge cases where after MAX_TIMER seconds, we just continue to the next job

## Other manual steps needed

Run script `main_linkedin.py` in debugging mode. When it crashes, if the chrome window is still open, manually sign in
to your linkedin account. If the chrome window is closed, run the script again, and pause the execution once the
chrome window is open. This gets around the "I'm not a robot problem".

Manually apply for at least 1 job so you can enter in your resume. The code will use this resume for other jobs

When you run the script at first it is not going to apply for any jobs as most jobs have mandatory questions that need
answered. Every time a question needs answered, it will be recorded into
autoapply/linkedin/text/unanswered_questions.txt The file is sorted by the number of times you have been asked the
questions. The questions will have their "fluff" removed, so miscellaneous words will not appear in the sentence.
This way "how many years of python experience do you have?" and "years of python experience?" will be recorded as the
same question. Answer the questions in the file like so (question, answer, times asked)

```commandline
software development,,93.0 <- Question is how many years of software development experience do you have? It has been 
asked 93 times. 

software development,6,93.0 <- I have 6 years of experience
 
```

Some questions are multiple choice, in that case, the choices are separated with a "^" character. Example

```
Choices are no or yes here
"are a us citizen, lawful permanent resident, green card holder, or asylee/refugee:select an option^no^yes",,123.0
```

When you answer the questions, save the file. The code will then take the answered questions out of the file and
save them into `questions.txt`

### Text files

Record some statistics into the text file you have

- applied_for.csv - list of urls with the jobs you've applied for
- stats.txt - record average time taken to apply for job. Percentage of jobs applied for (vs unable to apply because
  of errors)