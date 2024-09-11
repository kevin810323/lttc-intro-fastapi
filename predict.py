import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
dirname = os.path.dirname(__file__)
import spacy
en_nlp = spacy.load('en_core_web_sm')
import errant
annotator = errant.load("en", nlp = en_nlp)

T5_GEC_LEC = 't5_gec_lec'
PREFIX = 'correct this: '

geclec_t5_path = os.path.join(dirname, T5_GEC_LEC)
geclec_t5_tok = AutoTokenizer.from_pretrained(geclec_t5_path)
geclec_t5_model = AutoModelForSeq2SeqLM.from_pretrained(geclec_t5_path)


    
def predict(text): 
    text=text.strip()
    doc = en_nlp(text)
    sent_list=[ s.text for s in  doc.sents]
    #print(sent_list)
    if IsWrongEnter(sent_list):
        return status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE
    geclec_sent = correct_many_sents(sent_list)
    ori = annotator.parse(text, tokenise=True)  
    cor = annotator.parse(geclec_sent, tokenise=True)  
    edits = annotator.annotate(ori, cor, lev=True, merging="all-merge")
    return {"ori": text, "cor": geclec_sent, "edits":edits, "doc":doc}

def IsWrongEnter(sent_list:list):
    for sent in sent_list:
        if len(sent)>512:
            return True
    return False


def correct_sent(sent) -> str:
    input_ids = geclec_t5_tok(f"{PREFIX}{sent}", return_tensors='pt').input_ids
    outputs = geclec_t5_model.generate(input_ids, max_length=200)
    output_sent = geclec_t5_tok.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return output_sent


def correct_many_sents(sent_list) -> str:
    output_sents = []
    for sent in sent_list:
        if sent=='':
            continue
        sent=sent+'.'
        output = correct_sent(sent)
        output_sents.append(output)
    return ' '.join(output_sents)
 