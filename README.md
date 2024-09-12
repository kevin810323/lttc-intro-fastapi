# lttc-intro-fastapi
This is the api for grading LTTC 初級 test.

Before running the api, please done the following:
1. download the required packages by calling requirement.txt
pip install --user -r requirement.txt

2. download the gec model from Google doc and unpack in project dir
https://drive.google.com/file/d/1qPvh9dWr99tCP8aAgh1BPuw6MmcpeL-g/view?usp=sharing



Call the api:
/grade/ : input a json test file and return the graded test
/session/ : return the current version

json input example:
```json
{
    "test_id": 1,
    "short-answer-questions" : {
        "Q1" : {
            "orig": "Mary _ her children the story now.",
            "c_ans" : ["Mary is telling her children the story now.",
                        "Mary is not telling her children the story now.",
                        "Mary is going to tell her children the story now.",
                        "Mary is not going to tell her children the story now.",
                        "Mary won't tell her children the story now."],
            "s_ans" : "Mary tells her children the story now."
        },
        "Q2" : {
            "orig": "What _ for lunch yesterday?",
            "c_ans" : ["What did John have for lunch yesterday?",
                        "What did John eat for lunch yesterday?"],
            "s_ans" : "What did John have for lunch yesterday?"
        },
        "Q3" : {
            "orig": "This is _ room in the office.",
            "c_ans" : ["This is the brightest room in the office."],
            "s_ans" : "This is the most bright room in the office."
        },
        "Q4" : {
            "orig": "The students will give _ their teacher.",
            "c_ans" : ["The students will give a card to their teacher."],
            "s_ans" : "The students will give a card to their teacher."
        },
        ...

    },

    "short_essay": {
        "text": "Last Saturday, Nacy's mom took her to the hair salon. Nancy said she want to cut hair as same as the picture. But when she got up, she cried loudly. Because the hair style was not she wanted. Then Nacy and her mom got home. Her mom said don't cry and can wear the hat to her.", 
        "sample": "Nancy's mother took her to a hair salon last Saturday. Nancy showed the woman a picture of  the hair style she wanted. Then the woman cut her hair. Nancy cried when she saw her hair in the mirror. When they got home, Nancy's mother gave Nancy a hat. She hoped that Nancy would stop crying."

    }
}
```


json output example:

``` json

{
    "short-answer-questions": {
        "Q1": {
            "c_ans": [
                "Mary is telling her children the story now.",
                "Mary is not telling her children the story now.",
                "Mary is going to tell her children the story now.",
                "Mary is not going to tell her children the story now.",
                "Mary won't tell her children the story now."
            ],
            "grade": 0,
            "orig": "Mary _ her children the story now.",
            "s_ans": "Mary tells her children the story now."
        },
        "Q2": {
            "c_ans": [
                "What did John have for lunch yesterday?",
                "What did John eat for lunch yesterday?"
            ],
            "grade": 2,
            "orig": "What _ for lunch yesterday?",
            "s_ans": "What did John have for lunch yesterday?"
        },
        "Q3": {
            "c_ans": [
                "This is the brightest room in the office."
            ],
            "grade": 0,
            "orig": "This is _ room in the office.",
            "s_ans": "This is the most bright room in the office."
        },
        "Q4": {
            "c_ans": [
                "The students will give a card to their teacher."
            ],
            "grade": 2,
            "orig": "The students will give _ their teacher.",
            "s_ans": "The students will give a card to their teacher."
        }
    },
    "short_essay": {
        "corrected_essay": "Last Saturday, Nacy's mom took her to the hair salon. Nancy said she wanted to cut her hair the same as the picture. But when she got up, she cried out loudly. Because the hairstyle was not what she wanted. Then Nacy and her mom got home. Her mom said don't cry and you can wear the hat to her.",
        "edited_essay": "Last Saturday , Nacy 's mom took her to the hair salon . Nancy said she [- want -] [+ wanted +] to cut [+ her +] hair [- as -] [+ the +] same as the picture . But when she got up , she cried [+ out +] loudly . Because the hair style was not [+ what +] she wanted . Then Nacy and her mom got home . Her mom said do n't cry and [+ you +] can wear the hat to her.",
        "essay_score": "4.0",
        "orig_essay": "Last Saturday, Nacy's mom took her to the hair salon. Nancy said she want to cut hair as same as the picture. But when she got up, she cried loudly. Because the hair style was not she wanted. Then Nacy and her mom got home. Her mom said don't cry and can wear the hat to her."
    },
    "test_id": 11
}

