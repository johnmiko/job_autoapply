import re


def question_is_generic(question_text, url):
    text = question_text.lower()
    if is_previous_employee(text):
        return answer_previously_employed_by_company()
    elif 'salary' in text:
        return answer_salary_question(url)
    elif is_allowed_to_work_in_canada(text):
        return 'yes'
    elif 'gender' in text:
        return 'male'
    elif 'disability' in text:
        return 'yes'
    return 'answer not found'


def is_allowed_to_work_in_canada(text):
    return (re.search('legally.*to work.*canada', text)) or (re.search('eligible.*to work.*canada', text))


def is_previous_employee(text):
    return ('previously been employed' in text) \
        or (re.search('are currently a.*employee', text)) \
        or ("êtes-vous présentement à l'emploi de" in text)


def answer_salary_question(url):
    if 'developer' in url:
        return 125000
    # elif 'assistant' in url:
    else:
        salary = 125000
    return salary


def answer_previously_employed_by_company():
    return 'No'


def gender(question_text):
    text = question_text.lower()


"""
salary
how much compensation are looking for this role,,13.0
what are your annual salary expectations,,13.0

write cover letter
briefly describe how your experience applies to the job description for this role.,,13.0

are currently a paper employee:select an option^no^yes,,19.0
"if chose other for how heard about this opportunity, please specify how heard about it/ si vous choisissez «autre» pour comment avez-vous entendu parler de cette opportunité, veuillez spécifier de quelle façon vous en avez entendu parler",,15.0
"race/ethnicity - gender, race and ethnicity (definitions):select an option^american indian or alaska native^asian^black or african american^hispanic or latino^native hawaiian or other pacific islander^white^two or more races^prefer not to answer",white,15.0
solid ci/cd skills:select an option^yes^no,yes,15.0
are 18 years age or older:yes^no,,13.0
vivez-vous au canada:select an option^yes^no,yes,13.0 <- do you live in canada
"at least 5 years experience back-end development nodejs, typescript, or graphql:select an option^yes^no",yes,13.0
were aware sonder prior to applying:select an option^no^yes,,13.0
"""

# def answer_citizenship(question_text):
#     text = question_text.lower()
#     # what country are located in:select an option^canada/ canada^cyprus/ chypre^luxembourg/ luxembourg^romania/ roumanie^united states america / états-unis d'amérique^united kingdom/ royaume-uni^other / autre,,21.0
#     # are eligible to work canada:yes^no,,20.0
#     if text ==
#     'what country are located in'
# citizenship <- maybe this should go in a new text file?
