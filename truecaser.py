import string

def get_true_cases(words):
    cases = [] # list of tuples of booleans (True = lowercase, False otherwise)
    
    for word in words:
        if word not in string.punctuation:
            originallyLower = word.islower()
            nowLower = originallyLower
            if not originallyLower and word.lower() in cocoWordsWithCase:
                if word not in cocoWordsWithCase or cocoWordsWithCase[word.lower()] >= 10*cocoWordsWithCase[word]:
                    nowLower = True
            cases.append((originallyLower, nowLower))
        else:
            cases.append((True, True))
    
    newWords = []
    
    for i in range(len(words)):
        shouldStayUpper = False
        if cases[i] == (False, True):
            if i != 0 and cases[i-1][1] == False:
                shouldStayUpper = True
            elif i != len(cases)-1 and cases[i+1][1] == False:
                shouldStayUpper = True
                
        if shouldStayUpper or cases[i][0] == cases[i][1]:
            newWords.append(words[i])
        else:
            newWords.append(words[i].lower())
            
    return newWords