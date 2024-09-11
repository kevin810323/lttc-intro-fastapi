import errant
from itertools import chain
import spacy
import nltk
import requests
import json
from predict import predict
nltk.download('punkt')

en_nlp = spacy.load('en_core_web_sm')
annotator = errant.load("en", nlp = en_nlp)


"""
handle the issue of recognizing "every one" -> "everyone" as one error
"""
def merge_edits(edits):
    if len(edits) < 2:
        return edits
    
    #edits = [e for e in edits if "ORTH" not in e.type ]

    copy = edits.copy()
    for i in range(1,len(edits)):
        merge_str = edits[i-1].o_str + edits[i].o_str
        if edits[i].c_str == merge_str:
            copy.remove(edits[i-1])
            copy.remove(edits[i])
    
    return copy

"""
allowed_ans = [ [sent, [ [index], [2nd index], ... ] ], 
                [sent ...] ]
[['We bought two bottles of wine for the party.', [[2, 3, 4, 5]]]]

"""
def grader(allowed_ans, student_ans):
    ans_sents = [item[0] for item in allowed_ans]
    num_blanks = [len(item[1]) for item in allowed_ans]
    ans_blanks = [list(chain.from_iterable(item[1])) for item in allowed_ans]
    final_grade = 0
    final_edit = [None] * 10
    stud = annotator.parse(student_ans, tokenise=True)  
    
    for i, cand in enumerate(ans_sents):
        cand = annotator.parse(cand, tokenise=True)
        edits = annotator.annotate(stud, cand, lev=True, merging="all-split")
        edits = merge_edits(edits)
        temp_grade = 2
        temp_edits = []
        for edit in edits.copy():
            if "CONTR" not in edit.type and "SPACE" not in edit.type:
                temp_edits.append(edit)
                if edit.c_start in ans_blanks[i]:
                    if "SPELL" in edit.type:
                        temp_grade -= 1
                        continue
                    if num_blanks[i] == 1:
                        if "PREP" in edit.type or "DET" in edit.type or "PUNCT" in edit.type:
                            temp_grade -= 1
                        else:
                            temp_grade -= 2
                    else:
                        temp_grade -= 1
                else:
                    temp_grade -= 0.5
            else:
                edits.remove(edit)

        final_grade = max(final_grade, temp_grade)          
        if len(final_edit) > len(temp_edits):
            final_edit = temp_edits

        if final_grade == 0.5:
            final_grade = 0
        if final_grade == 1.5:
            final_grade = 1
    return {"grade" : final_grade, "edits" : final_edit}


def gec_result(text):
    gec = predict(text)
    print(gec)
    doc = gec['doc']
    edits = gec["edits"]
    for e in edits:
        print("Edits: \n")
        print(e.o_start, e.o_end, e.o_str, e.c_start, e.c_end, e.c_str, e.type)
    edits = merge_edits(edits)

    i = 0
    j = 0
    s = ""
    if len(edits) > 0:
        while i < len(doc):
            if edits[j].o_start > i:
                s = s  + doc[i].text + " "
                i += 1
            elif edits[j].o_start == i:
                if edits[j].o_str:
                    s = s + "[- " + edits[j].o_str + " -] "
                    
                if edits[j].c_str:
                    s = s + "[+ " + edits[j].c_str + " +] "
                
                if j + 1 < len(edits):
                    i = edits[j].o_end
                    j += 1
                
                else:
                    toks = doc[edits[j].o_end:].text
                    s = s + toks
                    break
    else:
        s = text

    return {"edited_essay": s, "orig_essay": text, "corrected_essay": gec['cor']}


def identify_blank(question, answer):
    blank = []
    j = 0
    temp = []
    f = False
    answer = en_nlp(answer)
    question = en_nlp(question)
    for i, tok_a in enumerate(answer):
        if answer[i].text == question[j].text:
            if f:
                f = False
                blank.append(temp)
                temp = []
            j += 1
            continue
        if question[j].text == "_":
            f = True
            j += 1

        temp.append(i)
    return blank

def update_answers(question, c_ans):
    AnswerList = []
    for j, ans in enumerate(c_ans):
        blank = identify_blank(question, ans)
        AnswerList.append([ans, blank])
    
    return AnswerList
