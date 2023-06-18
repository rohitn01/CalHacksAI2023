import openai
import json

openai.api_key = "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"

def chatGPT(prompt, model_engine="text-davinci-003", max_tokens = 1024):
  completion = openai.Completion.create(
      engine=model_engine,
      prompt=prompt,
      max_tokens=max_tokens,
      temperature=0.3,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
      )
  return completion.choices[0].text

def get_question(class_name, topic, num_q):
  question_prompt = "Acting as a friend in my college class called " + class_name + ", " +\
  "engage with me in constructive discussion and exmplain in simple and understandable terms what " + topic +\
  " is in two sentences, and generate " + str(num_q) + " short answer question" + ("s" if num_q > 1 else "") + " to test my understanding."
  tone_prompt = "Use a friendly tone and stimulate my intellectual curiosity."
  formatting_prompt = '''
  Return the response in the following JSON format (only return JSON and do not put any plain text in the response): 
    {
      "summary": <the summary>,
      "questions" : [
        <question1>,
        <question2>,
      ]
    }
    '''
  return (question_prompt + "\n" + tone_prompt, formatting_prompt)

def get_answer(Q, answers):
  intro_prompt = "Given that you just asked the user these questions: "
  answer_prompt = "And the user responds to each question according to the following:"
  for i, ans in enumerate(answers):
    answer_prompt += "\n"
    answer_prompt += "Answer to question " + str(i) + ": "
    answer_prompt += '"' + ans + '"'
  generate_prompt = "Critically evaluate and break down the user's response in a constructive manner. For the correctness rating put either 'Correct', 'Partially Correct', or 'Incorrect'. Do not just give the right answer. Try to explore further implications of the question but keep responses to five sentences or fewer."
  tone_prompt = '''Speak from a second person perspective, address to the user as 'you' and the user's response as 'your response', and ensure your responses to each question are contained in each 'response' field.
  Don't speak in a robotic tone, speak like a friendly tutor who has a secret crush on you and be VERY conversational.
  '''
  format_prompt = '''Return the response in the following JSON format (only return JSON and do not put any plain text in the response): 
  {"answers": [
    {
      "rating": <put the correctness rating to the first question here>,
      "explanation": <put the response to the first question here>
    },
    {
      "rating": <put the correctness rating to the second question here>,
      "explanation": <put the response to the second question here>
    }
  ]
  }'''
  prompt = intro_prompt + '\n"' + Q + '"\n' + answer_prompt + "\n" + generate_prompt + '\n' + tone_prompt + '\n' + format_prompt
  return prompt
