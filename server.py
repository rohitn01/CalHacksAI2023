import os
from http.client import responses
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from gpt_client import chatGPT, get_question, get_answer
from markupsafe import escape
import json


# CHANGE WHEN PRESENTING FOR UPLOAD FOLDER
UPLOAD_FOLDER = str(os.getcwd()) + '/pdf_uploads'
ALLOWED_EXTENSIONS = {'pdf'}
NUM_QUESTIONS_ASKED = 5

app = Flask(__name__)
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

@app.route('/homehandler', methods=['GET', 'POST'])
def home_handler():
    return redirect(url_for('test', request=request))

@app.route('/generate-reviews', methods=['GET', 'POST'])
def handle_human_answers():
       questions = request.form['questions']
       answers = request.form['answers']

       gpt_chat = get_answer(questions, answers)
       response_json = chatGPT(gpt_chat)
       print("afhbjafja", response_json)
       response = json.loads(response_json)
       return response
       #redirect(url_for('home_handler', request=response))

       '''
       gpt_quiz_feedback = response["answers"]
       #prompt_response = gpt_quiz_feedback
       prompt_response = "Provide feedback"
       '''

@app.route('/generate-questions/<request>', methods=['POST', 'GET'])
def test(request):
    print("Workig sg")
    ex = [
    "What is the smallest unit of life?",
    "What processes do cells carry out?",
    "What are cells made of?",
    "How do cells work together to make life possible?",
    "What are the different types of cells?"
  ]
    return render_template("ask-users.html", questions=ex)

'''
@app.route('/generate-questions/<request>', methods=['GET', 'POST'])
def generate_questions(request):
    global user_topic
    global user_class
    global NUM_QUESTIONS_ASKED
    global R
    global Q
    if request.method == 'POST':
        user_topic = request.form['topic']

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('download_file', name=filename))
        

        
        #Embedding logic with FeatureForm must be connected
        
        user_class = "Default Class"
        
        Q, R = get_question(user_class, user_topic, NUM_QUESTIONS_ASKED)
        response_json = chatGPT(Q + R)
        print(response_json)
        response = json.loads(response_json)
        questions = response["questions"]
        return render_template('ask-users.html', questions=questions)
'''


'''
@app.route('/get_response', methods=['POST'])
def get_response():
    global inital_prompts_filled
    global user_class
    global user_topic
    global user_q_count
    global questions
    global answers
    global curr_question_response
    global R
    global Q
    global gpt_quiz_feedback

    user_message = escape(request.form['user_message'])
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
        prompt_response = response["summary"] + "\n\n" + questions[0]
    elif inital_prompts_filled > 3:
        answers.append(user_message)
        curr_question_response += 1

        if(curr_question_response <= len(questions)):
            prompt_response = questions[curr_question_response - 1]
        else:
            gpt_chat = get_answer(Q, answers)
            response_json = chatGPT(gpt_chat)
            print("afhbjafja", response_json)
            response = json.loads(response_json)
            gpt_quiz_feedback = response["answers"]
            #prompt_response = gpt_quiz_feedback
            prompt_response = "Provide feedback"



    inital_prompts_filled += 1
    return {'response': prompt_response}
'''

'''
@app.route('/update_chat', methods=['POST'])
def update_chat():
    global gpt_quiz_feedback
    global answers
    global questions
    chat_data = request.json.get('chatData')  
    print("Lengeth chat data:", len(chat_data))
    updated_chat_data = []
    new_answers = [chat_data[i]  for i in range(len(chat_data) + 1 - (2 * len(answers)), len(chat_data), 2)]
    new_questions = [chat_data[i] for i in range(len(chat_data) - (2 * len(questions)), len(chat_data), 2)]
    for ques in range(questions):
        updated_chat_data.append(new_questions[ques])
        updated_chat_data.append(new_answers[ques])
        updated_chat_data.append(gpt_quiz_feedback[ques]["rating"])
        updated_chat_data.append(gpt_quiz_feedback[ques]["explanation"])

    chat_data = chat_data[0:len(chat_data) - (2 * len(answers))].extend(updated_chat_data)
    
    return {'status': 'success', 'chatData': chat_data}
'''

if __name__ == '__main__':
    inital_prompts_filled = 0
    answers = []
    app.run(debug=True)