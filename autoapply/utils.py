# import logging
#
# import pandas as pd
#
# from linkedin.wrappers import passTimeoutException
# from constants import QUESTION_FLUFF
#
#
# def get_questions_and_answers(QUESTIONS_FILE):
#     # Also reorders questions file
#     with open(QUESTIONS_FILE, 'r') as qf:
#         lines = []
#         for line in qf:
#             if ',' not in line:
#                 line = line.strip('\n') + ',\n'
#             # Missing answer
#             # if line.endswith(':\n'):
#             #     line = line[:-1] + '-1' + line[-1:]
#             lines.append(line)
#         # Remove duplicates if they exist and keep order
#         lines = list(dict.fromkeys(lines))
#
#     df = pd.read_csv(QUESTIONS_FILE, delimiter=',', header=None, encoding='latin1')
#     df3 = df.sort_values([1, 0], ascending=False)
#     # df3.to_csv(QUESTIONS_FILE, sep=',', header=None, index=False)
#     df3[0] = df3[0].str.lower()
#     for fluff in QUESTION_FLUFF:
#         df3[0] = df3[0].str.replace(fluff, '')
#     df3[0] = df3[0].str.strip()
#     df3 = df3.drop_duplicates(0)
#     df3.to_csv(QUESTIONS_FILE, sep=',', header=None, index=False, encoding='latin1')
#     # df3.to_csv('temp.txt', sep=',', header=None, index=False)
#     q_and_as = []
#     for line in lines:
#         q_and_as.append(line.strip('\n').split(','))
#
#     return q_and_as
#
#
# def create_logger(name, level=logging.INFO):
#     logger = logging.getLogger(name)
#     logger.setLevel(level)
#     c_handler = logging.StreamHandler()
#     c_handler.setLevel(level)
#     logger.addHandler(c_handler)
#     logger.debug(f'created logger {logger.name}')
#     return logger, c_handler
#
#
# def is_radio_button_question(question):
#     return len(question.find_elements('xpath', ".//input")) == 2
#
#
# @passTimeoutException
# def use_latest_resume(dm):
#     choose_resume_els = dm.find_elements('xpath', 'button', 'aria-label', 'Choose Resume', 2)
#     latest_resume = choose_resume_els[-1]
#     latest_resume.click()
