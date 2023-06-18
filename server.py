from flask import Flask, render_template, request
from gpt import *

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
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
        user_q_count = user_message
        question_prompt = get_question(user_class, user_topic, user_q_count)
        json_response = chatGPT(question_prompt)
        question_dict = json.load(json_response)
        prompt_response = question_dict
    inital_prompts_filled += 1
    return {'response': prompt_response}

if __name__ == '__main__':
    inital_prompts_filled = 0
    app.run(debug=True)