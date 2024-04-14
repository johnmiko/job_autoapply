# import pandas as pd
import pandas as pd

from autoapply.linkedin import QUESTIONS_FILE

# may want to just add a category into the questions file, start here for now
df = pd.read_csv(QUESTIONS_FILE, delimiter=',', encoding='latin1')
# not skills
df['category'] = 'skill'
misc = ['city', 'bachelor', 'street address', 'english', 'how did hear about this job', 'phone country code', 'e-mail',
        'visa', 'zip', 'postal code', 'postal', 'sponsorship', 'numéro de téléphone', 'legally authorized',
        'comfortable', 'disability', 'gender', 'race', 'resident', 'citizen', 'email', 'identification', 'countries',
        'teléfono', 'eligible', 'compensation', 'register', 'race', 'linkedin', 'veteran', 'Quebec',
        'what state or territory', 'quel est votre niveau en français', 'immigration', 'privacy notice']
df.loc[df['question'].str.contains('|'.join(misc)), 'category'] = 'misc'
df2 = df[df['category'] == 'skill']
df2.to_csv('text/requested_skills.txt', header=True, index=False)
