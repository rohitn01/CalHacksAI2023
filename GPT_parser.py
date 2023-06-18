import json
import requests
from gpt_response import GPTResponse
def parse_response(input):
    response_dict = json.loads(input)

    summary = response_dict["summary"]
    questions = response_dict["questions"]

    return GPTResponse(summary, questions)

