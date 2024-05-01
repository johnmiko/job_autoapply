import re
import time
from contextlib import suppress

import pandas as pd
from more_itertools import always_iterable
from selenium.common import NoSuchElementException, InvalidElementStateException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from autoapply.linkedin.constants import QuestionType, QUESTION_FLUFF
from autoapply.linkedin.inputs import REFERENCES_FILE, GUESS_0_FOR_UNANSWERED, UNANSWERED_QUESTIONS_FILE, \
    PAUSE_AFTER_ANSWERING_QUESTIONS
from autoapply.linkedin.utils import logger, remove_fluff_from_sentence, \
    put_answer_in_question_textbox, should_pause, get_question_type, clean_question_text, translate_answer_to_french


def question_mapper(question_text):
    text = question_text.lower()
    if is_previous_employee(text):
        return "previously been employed by this company"
    elif 'salary' in text:
        return "salary"
    elif is_allowed_to_work_in_canada(text):
        return "allowed to work in canada"
    elif 'gender' in text:
        return "what is your gender"
    elif 'disability' in text:
        return "do you have a disability"
    elif "how did hear" in text:
        "how did you hear about us"
    return question_text


def question_is_generic(question_text):
    text = question_text.lower()
    if is_previous_employee(text):
        return "previously been employed by this company", "No"
    elif 'salary' in text:
        return "salary", "130000"
    elif is_allowed_to_work_in_canada(text):
        return "allowed to work in canada", 'yes'
    elif 'gender' in text:
        return "what is your gender", 'male'
    elif 'disability' in text:
        return "do you have a disability", 'yes'
    elif "how did hear" in text:
        return "how did you hear about us", "linkedin"
    elif "how did you hear" in text:
        return "how did you hear about us", "linkedin"
    elif "veteran" in text:
        return "are you a veteran", ["no", "I am not a protected veteran"]
    # elif ("ethnicity" in text) or ("race" in text):
    elif any(substring in text for substring in ["ethnicity", "race"]):
        return "race", ["white", "White (Not Hispanic or Latino)"]
    return 'question not found', 'answer not found'


def is_allowed_to_work_in_canada(text):
    return (re.search('legally.*to work.*canada', text)) or (re.search('eligible.*to work.*canada', text))


def is_previous_employee(text):
    return ('previously been employed' in text) \
        or (re.search('are currently a.*employee', text)) \
        or ("êtes-vous présentement à l'emploi de" in text)


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
def answer_questions(dm, questions, tried_to_answer_questions, q_and_as_df, QUESTIONS_FILE, old_questions, url):
    if not tried_to_answer_questions:
        for question in questions:
            # if not question_is_required(question.text):
            #     continue
            # Drop down menu question/select
            # Issue if question is side by side
            logger.debug('\n' + question.text.replace("\n", " - "))
            logger.debug(f'{question.tag_name=}')
            q_m = QuestionManager(question)
            q_text = q_m.q_text
            question_type = q_m.question_type
            question_is_new = True
            q_text = remove_fluff_from_sentence(q_text)
            logger.debug(question.text)
            question_mapped = question_mapper(question.text)
            if question_mapped != question.text:
                q_text = question_mapped
            generic_question, generic_answer = question_is_generic(question.text)
            if generic_answer != 'answer not found':
                q_m.text = generic_question
                q_m.answer_question(generic_answer)
                continue
            if 'by checking this box' in question.text.lower():
                options = question.find_elements('xpath', ".//label")
                options[0].click()  # Just check the box
                continue
            if ("references" in q_text) and ("preferences" not in q_text):
                with open(REFERENCES_FILE, "r") as f:
                    references = f.read()
                q_m.answer_question(references)
            # q_text cn be "citycity" for some reason
            if (q_text == "city") or (q_text == "citycity"):
                put_answer_in_question_textbox('Montreal, Quebec, Canada', question)
                # For city question, need to click the box to continue
                with suppress():
                    dm.find_element('jobs-easy-apply-content').click()
                    time.sleep(0.5)
                continue
                # try:
                #     questions = WebDriverWait(question, 1).until(
                #         lambda question: question.find_elements('xpath', '//div[@role="listbox")]'))
                #     dropdown = WebDriverWait(question, 1).until(
                #         lambda question: question.find_element('xpath', "//ul"))
                #     # select first choice
                #     ActionChains(dm.driver).move_to_element(dropdown).click(button).perform()
                #     WebDriverWait(dropdown, 1).until(
                #         EC.element_to_be_clickable((By.XPATH, "//li"))).click()
                # except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                #     continue
            question_formatted = q_text.split(':')[0].replace('"', '')
            if "veteran" in q_text:
                a = 1
            for index, row in q_and_as_df.iterrows():
                existing_question, existing_answer, times_asked = row[['question', 'answer', 'times_asked']]
                existing_question_formatted = str(existing_question).lower().split(':')[0].replace('"', '')
                if existing_question_formatted == question_formatted:
                    # Can switch to this now
                    logger.debug("q_and_as_df[q_and_as_df['question'] == question_formatted]")
                    logger.debug(q_and_as_df[q_and_as_df['question'] == question_formatted])
                    q_and_as_df.at[index, 'times_asked'] += 1
                    # https://www.linkedin.com/jobs/search/?currentJobId=3294737126&f_AL=true&f_E=2&f_JT=P%2CC%2CT%2CF&f_WT=1%2C2%2C3&geoId=101330853&keywords=it%20support&location=Montreal%2C%20Quebec%2C%20Canada&refresh=true&start=6
                    if (pd.isna(existing_answer)) or (existing_answer == ''):
                        logger.info(f'\tquestion found but no answer: "{existing_question}"')
                        break
                    answer = existing_answer.strip().lower()
                    # Answers are being recorded as floats, so convert to ints if we can
                    # Floats are not accepted
                    with suppress(ValueError):
                        answer = int(float(answer))
                    q_m.answer_question(answer)
                    # if question_type == QuestionType.text:
                    #     put_answer_in_question_textbox(answer, question)
                    # elif question_type == QuestionType.dropdown:
                    #     put_answer_in_question_dropdown(answer, text_options)
                    #     try:
                    #         index = text_options.index(answer)
                    #     except ValueError:  # ("if it's not found in the list")
                    #         continue
                    #     select.select_by_index(index)
                    # elif question_type == QuestionType.radio:
                    #     options = question.find_elements('xpath', ".//label")
                    #     answer_found = False
                    #     for option in options:
                    #         option_text = option.text.lower()
                    #         for fluff in QUESTION_FLUFF:
                    #             option_text = option_text.replace(fluff, '')
                    #         if ('oui' in option_text) or ('non' in option_text):
                    #             answer = translate_answer_to_french(answer)
                    #         if option.text.lower() == str(answer).lower():
                    #             answer_found = True
                    #             break
                    #     if not answer_found:
                    #         logger.info(f'\tdid not find answer for radio question {q_text}')
                    #     else:
                    #         option.click()
                    # else:
                    #     raise ValueError('question type unknown ' + question_type)
                    # # Unique case of textbox + dropdown
                    question_is_new = False
                    break
            if question_is_new:
                if (question_type == QuestionType.dropdown) or (question_type == QuestionType.radio):
                    if question_type == QuestionType.dropdown:
                        select = Select(question.find_elements('xpath', ".//select")[0])
                        text_options = [option.text.lower() for option in select.options]
                    elif question_type == QuestionType.radio:
                        options = question.find_elements('xpath', ".//label")
                        text_options = [option.text.lower() for option in options]
                    q_text = q_text + ':' + "^".join(text_options)
                else:
                    # if question_type == QuestionType.text:
                    try:
                        text_box = question.find_element('xpath', ".//input")
                    except NoSuchElementException:
                        text_box = question.find_element('xpath', ".//textarea")
                    with suppress(InvalidElementStateException):
                        text_box.clear()
                    if GUESS_0_FOR_UNANSWERED:
                        text_box.send_keys(0)
                try:
                    q_text2 = q_text.encode('latin1', 'ignore').decode("latin1").replace('"', '\"')
                    q_and_as_df = pd.concat([q_and_as_df, pd.DataFrame({'question': [q_text2]})])
                    logger.info(f'\tnew question: "{q_text2}"')
                    logger.info(f'\tnew question: "{question.text}"')
                except UnicodeEncodeError:
                    # Got error when question was in arabic
                    continue
        # Check that old_questions are not [], and questions don't match
        # We failed to answer questions if the page of questions is the same
        tried_to_answer_questions = old_questions and (questions == old_questions)
        if tried_to_answer_questions:
            old_questions = []
        else:
            old_questions = questions
    # update questions files
    q_and_as_df = q_and_as_df.sort_values('times_asked', ascending=False)
    df4 = q_and_as_df[q_and_as_df['answer'].isna()]
    df5 = q_and_as_df[~q_and_as_df['answer'].isna()]
    try:
        df4.to_csv(UNANSWERED_QUESTIONS_FILE, sep=',', header=True, index=False, encoding='latin1')
    except PermissionError:
        time.sleep(2)
        df4.to_csv(UNANSWERED_QUESTIONS_FILE, sep=',', header=True, index=False, encoding='latin1')
    try:
        df5.to_csv(QUESTIONS_FILE, sep=',', header=True, index=False, encoding='latin1')
    except PermissionError:
        time.sleep(1)
        df5.to_csv(QUESTIONS_FILE, sep=',', header=True, index=False, encoding='latin1')
    should_pause(PAUSE_AFTER_ANSWERING_QUESTIONS, "pause after answering questions")
    return tried_to_answer_questions, old_questions


class PhraseMatcher:
    def __init__(self, phrases: str | list, possible_matches: list):
        if isinstance(phrases, str):
            phrases = [phrases]
        self.phrases = phrases
        self.possible_matches = possible_matches
        self.similarities = []
        self.similarity_matrices = None

    def calculate_similarity_matrices(self):
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.possible_matches + self.phrases)
        matrices = []
        for p in tfidf_matrix[-len(self.phrases):]:
            similarity_matrix = cosine_similarity(tfidf_matrix[:-len(self.phrases)], p)
            matrices.append(similarity_matrix)
            similarity = [(phrase, similarity[0]) for phrase, similarity in zip(self.possible_matches,
                                                                                similarity_matrix)]
            self.similarities.append(similarity)
        self.similarity_matrices = matrices
        return matrices

    def find_closest_phrases(self):
        similarity_matrices = self.calculate_similarity_matrices()
        closest_phrases = []
        for similarity_matrix in similarity_matrices:
            closest_index = similarity_matrix.argmax()
            closest_phrases.append((self.possible_matches[closest_index]))
        return closest_phrases


def put_answer_in_question_dropdown(correct_answers, text_options, select):
    answer_found = False
    for correct_answer in always_iterable(correct_answers):
        with suppress(ValueError):  # if exact match is not found
            index = text_options.index(correct_answer)
            select.select_by_index(index)
            answer_found = True
    if not answer_found:
        # difflib.get_close_matches(correct_answer, text_options, n=3, cutoff=0.6)
        phrase_matcher = PhraseMatcher(correct_answers, text_options)
        closest_phrases = phrase_matcher.find_closest_phrases()
        closest_phrase = closest_phrases[0]
        index = text_options.index(closest_phrase)
        select.select_by_index(index)


class QuestionManager:
    def __init__(self, question_element: WebElement):
        self.element = question_element
        self.text = question_element.text.lower()
        self.question_type = get_question_type(question_element)
        question_text = self.text
        if self.question_type == QuestionType.radio:
            question_text = question_text.lower().split('required')[0].strip()
        q_text = clean_question_text(question_text)
        if self.question_type == QuestionType.dropdown:
            q_text = q_text.split('select an option')[0].strip()
        self.q_text = q_text

    def answer_question(self, answers: list | str):
        if not isinstance(answers, list):
            answer = answers
        if self.question_type == QuestionType.text:
            put_answer_in_question_textbox(answer, self.element)
        elif self.question_type == QuestionType.dropdown:
            select = Select(self.element.find_elements('xpath', ".//select")[0])
            text_options = [option.text.lower() for option in select.options]
            put_answer_in_question_dropdown(answer, text_options, select)
            with suppress(ValueError):  # ("if it's not found in the list")
                index = text_options.index(answer)
                select.select_by_index(index)
        elif self.question_type == QuestionType.radio:
            if isinstance(answers, str):
                answers = [answer]
            else:
                answers = [str(answer).lower() for answer in answers]
            options = self.element.find_elements('xpath', ".//label")
            answer_found = False
            for option in options:
                option_text = option.text.lower()
                for fluff in QUESTION_FLUFF:
                    option_text = option_text.replace(fluff, '')
                if ('oui' in option_text) or ('non' in option_text):
                    answer = translate_answer_to_french(answer)
                if option.text.lower() in answers:
                    answer_found = True
                    break
            if not answer_found:
                logger.info(f'\tdid not find answer for radio question {self.text}')
            else:
                option.click()
        else:
            raise ValueError('question type unknown ' + self.question_type)
