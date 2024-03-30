import os
import shutil
from os import listdir
from os.path import isfile, join

import pandas as pd

from cover_letter.inputs import COVER_LETTER_TEXT_DIR
from cover_letter.utils import get_posting_lines

pd.options.display.width = 0
posting = 'job_posting.txt'
company = 'Circle Medical'
job_title = 'Senior Data Engineer'
company_dir = f'{COVER_LETTER_TEXT_DIR}postings/{company.lower().replace(" ", "_")}/'
job_title_as_path = job_title.lower().replace(" ", "_")
job_title_fname = f'{job_title_as_path}.txt'
fname = f'{company_dir}{job_title_fname}'
if not os.path.exists(company_dir):
    os.makedirs(company_dir)

files = [f for f in listdir(company_dir) if isfile(join(company_dir, f))]
multiple_jobs_at_company = False
folder = company_dir + job_title_as_path
if not os.path.exists(folder):
    os.makedirs(folder)
for f in files:
    if f not in ['generated.txt', 'sent.txt', job_title_fname]:
        multiple_jobs_at_company = True
        fname = f'{folder}/posting.txt'
        if not os.path.isfile(fname):
            shutil.copyfile(posting, fname)
        break

if not multiple_jobs_at_company:
    if not os.path.isfile(fname):
        shutil.copyfile(posting, fname)
# posting_parts = posting.split('/')
# folder = '/'.join(posting_parts[:2])
# company = posting_parts[1]
# job_title = posting_parts[2].split('.')[0].replace('_', ' ')

lines = get_posting_lines(posting)
df_responses = pd.read_csv('responses.txt')
# df_responses['text'] = df_responses['text'].apply(literal_eval)
# df_responses['text_lower'] = df_responses['text'].str.lower()
df_responses['text'] = df_responses['text'].astype(str)
df_responses['text_lower'] = df_responses['text'].str.lower().str.split(',')
df_responses['text_regex'] = df_responses['text_lower'].str.join("|")
responses = []
df_use = pd.DataFrame()
# throw out everything before Responsibilities
start = True
start_line = 'qualifications'  # and Skills Required

for line in lines:
    if start:
        if line == '':
            continue
        words = line.strip().split(' ')
        new_words = []
        for word in words:
            if len(word) != 1:
                new_words.append(word)
        words_regex = '|'.join(new_words)
        words_regex = words_regex.replace(')', '\)').replace('(', '\(')
        # any(x in a_string for x in matches)
        # df['Names'].apply(lambda x: any([k in x for k in kw]))
        # Check if any words in posting line match phrases in response df
        df_match1 = df_responses.loc[df_responses['text_lower'].apply(lambda x: any([k in x for k in new_words]))]
        # Check if any phrases in respons df exist in posting line
        df_match2 = df_responses.loc[df_responses['text_lower'].apply(lambda x: any([k in line for k in x]))]
        # df_temp = df_responses.loc[df_responses['text_lower'].str.contains(words_regex)]
        if 'team' in words_regex:
            a = 1
        if not df_match1.empty:
            df_use = pd.concat([df_use, df_match1])
        if not df_match2.empty:
            df_use = pd.concat([df_use, df_match2])
    else:
        if start_line in line:
            print(start_line + ' found at line\n' + line)
            start = True
# gets upset about the lists
df_use = df_use.drop_duplicates('text')
if df_use.empty:
    print('no content created for cover letter')
    content = ''
else:
    df_years = df_use.loc[df_use['category'] == 'experience']
    df_years = df_years.reset_index(drop=True)
    df_years['years'] = df_years['response'].str.extract('(\d+)')
    df_years = df_years.sort_values('years', ascending=False)

    if len(df_years) == 2:
        years_of_exp_str = f"In terms of experience, I have {df_years.at[0, 'years']} years with {df_years.at[0, 'text']} and {df_years.at[1, 'years']} years with {df_years.at[1, 'text']}"
    else:
        df_years['str'] = df_years['years'] + ' with ' + df_years['text']
        years_of_exp_list = list(df_years['str'].values[1:])
        years_of_exp_str = f"In terms of raw experience, I have {df_years.at[0, 'years']} years with {df_years.at[0, 'text']}, " + ', '.join(
            years_of_exp_list)
    # elif len(df_years) == 3:
    #     join_with =
    #     years_of_exp_list.insert(-1, 'and')
    #     years_of_exp_str = ' '.join(years_of_exp_list)
    years_of_exp_paragraph = f"{years_of_exp_str}.\n"
    # TODO: using str to ignore "nan" value errors, should just handle them
    content = '\n'.join(df_use.loc[df_use["category"] != "experience", 'response'].astype(str).values)
    content = years_of_exp_paragraph + content
# I am writing to apply for the software developer position at Algolux. As a mechatronics engineer with experience in autonomous vehicles I believe I would be a great fit for this position.
intro = f"""Dear Hiring Manager, 

I am writing to apply for the {job_title} position at {company}. """
# mechatronics engineer
# p1 = """As a developer with 8 years of programming experience, I find the responsibilities of this job posting straightforward and enjoyable.\n"""
p1 = """As a developer with 8 years of programming experience, I believe I make an excellent candidate for this position.\n"""
outro = f"""
Please take a moment to look over my resume and schedule a meeting with me (https://calendly.com/johnmiko/meeting) so we can further discuss my qualifications for the {job_title} position. You can also reach me by email at johnmiko4@gmail.com. Thank you for taking the time to consider my application.

Sincerely,
 
John Miko
"""

cover_letter_text = intro + p1 + content + outro
with open(f'{folder}/generated.txt', 'w') as f:
    f.write(cover_letter_text)
