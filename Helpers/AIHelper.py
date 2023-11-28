import os
import time
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def getTaskTitle(message):
    retries = 0
    while retries < 5:
        try:
            a = "Make a clickup task title less than 13 words for the below message\n"
            a = a + message
            res = openai.Completion.create(
                model="text-davinci-003",
                prompt=a,
                max_tokens=512,
                temperature=0
            )
            return "[BUG] " + res["choices"][0]["text"].strip()
        except Exception as e:
            print(e)
            retries = retries + 1
            time.sleep(1)
    return None

def getTaskDescription(message):
    retries = 0
    while retries < 5:
        try:
            a = "Make a bug report for the below message\n"
            a = a + message
            res = openai.Completion.create(
                model="text-davinci-003",
                prompt=a,
                max_tokens=1000,
                temperature=0
            )
            return res["choices"][0]["text"].strip()
        except:
            retries = retries + 1
            time.sleep(1)
    return None
