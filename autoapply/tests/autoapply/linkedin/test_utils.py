# class Testget_questions_df:

# from app.utils import get_questions_df


# class TestThing(unittest.TestCase):
from autoapply.constants import PROJ_DIR
from autoapply.linkedin.utils import get_questions_df, answer_questions


def func2(x):
    return 5


def test_a():
    assert func2(4) == 2


def func(x):
    return x + 1


def test_answer():
    fname = 'tests/test_utils/test_questions_file.txt'
    fname = 'test_questions_file.txt'
    q_and_as_list = get_questions_df(fname)
    assert func(3) == 5


class Testanswer_questions:
    class MockSeleniumElement:
        text = 'email address'

        def find_elements('xpath', self, arg1):
            return [1]

        def find_element('xpath', self, arg1):
            return self

        def send_keys(self, keys):
            pass

        def clear(self):
            pass

    def test_answer_questions_doesnt_crash(self):
        fname = PROJ_DIR + '/tests/test_utils/test_questions_file.txt'
        unanswered_fname = PROJ_DIR + '/tests/test_utils/test_unanswered_questions_file.txt'
        questions = [self.MockSeleniumElement()]
        tried_to_answer_questions = False
        old_questions = []
        q_and_as_df = get_questions_df(fname, unanswered_fname)
        tried_to_answer_questions = answer_questions(questions, tried_to_answer_questions, q_and_as_df,
                                                     fname,
                                                     old_questions)


def test_get_questions_df():
    assert func(3) == 5
    a = 1
    fname = 'tests/test_utils/test_questions_file.txt'
    q_and_as_list = get_questions_df(fname)
    assert False == True


def test_questions_answers():
    questions = ['How many years of work experience do you have with Svelte?',
                 'What is your level of proficiency in English?\nWhat is your level of proficiency in English?\nRequired\n       Select an option\n       None\n       Conversational\n       Professional\n       Native or bilingual\n  ',
                 'How many years of experience in building real-time data-centric web applications?',
                 'Have you built client and server-side web socket-based applications?\nHave you built client and server-side web socket-based applications?\nRequired\n       Select an option\n       Yes\n       No\n   Please enter a valid answer',
                 'How many years of experience do you have building typescript web applications?']
