from http.client import responses
from flask import Flask, render_template, request
from gpt_client import chatGPT, get_question, get_answer
import json

app = Flask(__name__)
inital_prompts_filled = 0
user_class = None
user_topic = None
user_q_count = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global inital_prompts_filled
    global user_class
    global user_topic
    global user_q_count
    global questions
    global answers

    user_message = request.form['user_message']
    if inital_prompts_filled == 0:
        prompt_response = "Which class?"
    elif inital_prompts_filled == 1:
        user_class = user_message
        prompt_response = "What topic?"
    elif inital_prompts_filled == 2:
        user_topic = user_message
        prompt_response = "How many questions?"
    elif inital_prompts_filled == 3:
        user_q_count = int(user_message)
        Q, R = get_question(user_class, user_topic, user_q_count)
        response_json = chatGPT(Q + R)
        print(response_json)
        response = json.loads(response_json)
        questions = response["questions"]
        prompt_response = response["summary"] + "\n" + questions[0]
    elif inital_prompts_filled == 4:
        answers.append(user_message)
        prompt_response = questions[1]

    inital_prompts_filled += 1
    return {'response': prompt_response}

if __name__ == '__main__':
    inital_prompts_filled = 0
    answers = []
    app.run(debug=True)