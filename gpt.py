from openai import OpenAI 
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def get_recs_from_gpt(user_mood, user_artists): 
    msg = f'{user_mood} songs from {user_artists} in one list in the form \' artist - song \', no additional text, scramble the order, no quotation marks, at least 10 songs'
    resp = client.chat.completions.create(
        temperature=0.8,
        model='gpt-3.5-turbo', 
        messages = [
            {'role': 'user', 
             'content': msg}
        ])
    resp_content = resp.choices[0].message.content
    print(resp_content)

get_recs_from_gpt('sad', 'lauv, joji, rini')