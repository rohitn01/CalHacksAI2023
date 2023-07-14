import os
from http.client import responses
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from gpt_client import chatGPT, get_question, get_answer
from markupsafe import escape
import json

UPLOAD_FOLDER = str(os.getcwd()) + '/pdf_uploads'
SECRET_KEY = "secret-key"
ALLOWED_EXTENSIONS = {'pdf'}
NUM_QUESTIONS_ASKED = 5

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

inital_prompts_filled = 0
user_class = None
user_topic = None
user_q_count = None
answers = []
questions = None
R = None
curr_question_response = 1
gpt_quiz_feedback = None

@app.route('/')
def index():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/error')
def error():
    return render_template('page_not_found.html')
    
@app.route('/questions', methods=['GET', 'POST'])
def questions():
    
    #global user_topic
    global user_class
    global NUM_QUESTIONS_ASKED
    global R
    global Q
    
    if request.method == "POST":
        user_topic = request.form['topic']
        file = request.files['pdf']

        if file.filename == '':
            return redirect(url_for("error"))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)
        
        #Embedding logic with FeatureForm must be connected
        '''
        user_class = "Default Class"   
        Q, R = get_question(user_class, user_topic, NUM_QUESTIONS_ASKED)
        response_json = chatGPT(Q + R)
        print(response_json)
        response = json.loads(response_json)
        questions = response["questions"]
        '''
        
        #default questions for display sake. Comment out when embedding logic works
        questions = [
    
        "What was the percentage drop of African-American owned businesses due to the pandemic?",
        "What was the percentage drop of immigrant-owned businesses due to the pandemic?"  ]
    
        return render_template('questions.html', questions=enumerate(questions))

@app.route('/reveal_answers', methods=['GET', 'POST'])
def reveal_answers():
       global NUM_QUESTIONS_ASKED
       if request.method == "POST":           
            questions = []
            answers = []
            for key, value in request.form.items():
                if key.startswith("question"):
                    questions.append(value)
                elif key.startswith("answer"):
                    answers.append(value)
                print("Key: ", key, " Value: ", value)
            if len(questions) == 0 or len(answers) == 0:
                return redirect(url_for("error"))

            # GPT Chat logic for getting answer
            '''
            gpt_chat = get_answer(questions, answers)
            response_json = chatGPT(gpt_chat)
            print("afhbjafja", response_json)
            response = json.loads(response_json)
            '''
       
            #default questions for display sake. Comment out when GPT Chat logic works
            questions = [
            "What was the percentage drop of African-American owned businesses due to the pandemic?",
            "What was the percentage drop of immigrant-owned businesses due to the pandemic?"  ]
            answers = ["67", "80"]
            response = {"answers": [{
            "rating": "Partially Correct",
            "explanation": "Your response that African-American businesses saw a 67% drop is partially correct. The paper explains that the drop in African-American businesses was actually a percent drop, which is larger than your response. However, your response does provide indication that African-American business owners were hit especially hard. "
            },
            {
            "rating": "Incorrect",
            "explanation": "Your response that Latinx business owners saw an 80% drop is incorrect. According to the paper, Latinx business owners actually experienced a percent drop, which is lower than your response. Additionally, your response for the Asian business owners drop was also incorrect - the paper reports that Asian business owners actually dropped by percent, which is lower than your response. "
            }]}
        
            return render_template("return-results.html", questions=questions, answers=answers, gpt_reviews=response["answers"], zip=zip)

if __name__ == '__main__':
    inital_prompts_filled = 0
    answers = []
    app.run(debug=True)