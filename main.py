#from feature import StatisticalFeatureTransformer, ErrorFeatureTransformer
import pickle
from predict import predict
from utils import grader, gec_result, update_answers
from flask import Flask, jsonify, request
import pandas as pd
import spacy
import re
import logging
import logging.handlers
from evaluate import load
bertscore = load("bertscore")



from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict

FORMAT = '%(asctime)s %(levelname)s:%(message)s'
mylogger = logging.getLogger()
mylogger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler('data_storage/log.txt', maxBytes=1000000, backupCount=3)
handler.setFormatter(logging.Formatter(FORMAT))

mylogger.addHandler(handler)



VERSION = "Aug19"
en_nlp = spacy.load('en_core_web_sm')

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)


class Question(BaseModel):
    orig: str
    c_ans: List[str]
    s_ans: str
    grade = 0


class Test(BaseModel):
    test_id: int
    short-answer-questions: Dict[str, Question]
    short_essay: Dict[str, str]

app = FastAPI()


@app.get("/session/")
def default_response():
    return VERSION


@app.post("/grade/")
async def test_process():
    if request.is_json:
        data = request.json
        mylogger.info("Input data")
        mylogger.info(data)
        

        for qnum in data['short-answer-questions']:
            orig = data['short-answer-questions'][qnum]['orig']
            orig = re.sub("' s", "'s", orig)
            c_ans = data['short-answer-questions'][qnum]['c_ans']
            temp = []
            for ans in c_ans:
                temp.append(re.sub("' s", "'s", ans))
                
            
            allowed_ans = update_answers(orig, temp)

            s_ans = data['short-answer-questions'][qnum]['s_ans']
            s_ans = re.sub("' s", "'s", s_ans)
            grade = grader(allowed_ans, s_ans)
            data['short-answer-questions'][qnum]['grade'] = grade['grade']
            
        essay = data['short_essay']['text']
        sample = data['short_essay']['sample']

        topic_score = bertscore.compute(predictions=[essay], references=[sample], lang ='en', model_type="distilbert-base-uncased")['f1'][0]
        if topic_score < 0.7:
            essay_grade = 0
        elif len(en_nlp(essay)) < 50:
            essay_grade = 2
        else:
            df = pd.DataFrame({'text': [essay]}) 
            essay_grade = model.predict(df)[0]
        essay_result = gec_result(essay)
        essay_result['essay_score'] = essay_grade

        data["short_essay"] = essay_result
    
    else:
        mylogger.info("No json call")
        return "Not Json data"
    

    mylogger.info("Output data")
    mylogger.info(data)
    return jsonify(data), 200
