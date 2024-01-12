from openai import OpenAI 
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def get_recs_from_gpt(user_mood, user_artists): 
    num_artists = user_artists.count(',') + 1
    msg = f'{user_mood} songs from {user_artists} in one list in the form \' artist +-+ song \', no additional text, scramble the order, no quotation marks, at least {num_artists*5} songs'
    resp = client.chat.completions.create(
        temperature=0.3,
        model='gpt-3.5-turbo', 
        messages = [
            {'role': 'user', 
             'content': msg}
        ])
    resp_content = resp.choices[0].message.content
    return parse_gpt_result(resp_content)

def parse_gpt_result(resp_content):
    artist_and_songs = resp_content.splitlines()
    ret = [] #list of [song, artist]
    for line in artist_and_songs:
        split = line.split('+-+') #song +-+ 
        ret.append(split)

    return ret



