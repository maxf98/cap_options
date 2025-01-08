import os
from collections import defaultdict
import pickle
import openai
from time import sleep
from utils.cap_utils import extract_code, print_code



api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


TEMPERATURE = 1
MODEL = "gpt-4o"
MAX_TOKENS = 3000


def query_llm(messages):
    while True:
        try:
            response = client.chat.completions.create(
                    messages=messages,
                    temperature=TEMPERATURE,
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                )
            response = response.choices[0].message.content
            break

        except (openai.APIError) as e:
            print(f'OpenAI API got err {e}')
            print('Retrying after 10s.')
            sleep(10)

    return response


def parse_code_response(response):
    if '```' in response:
        code_str = extract_code(response)

    print_code(code_str)

    return code_str


def read_py(path_to_py):
    f = open(path_to_py, "r")
    return f.read()