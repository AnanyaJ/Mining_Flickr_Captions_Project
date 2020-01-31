import pickle
import nltk
from nltk.corpus import stopwords
stopWords = set(stopwords.words('english'))

def get_tokens(captions):
    '''Returns a list of lists with the words in each caption.'''
    tokenizedCaptions = []

    for caption in captions:
        words = []
        
        for word in caption.split(' '):
            letterPresent = False
            for char in word:
                if char.isalpha():
                    letterPresent = True
                    break
        
            if letterPresent:
                # removes punctuation
                while not word[-1].isalpha():
                    word = word[:-1]
                while not word[0].isalpha():
                    word = word[1:]
                
                words.append(word)
        
        if len(words) > 0:
            words[0] = words[0].lower()
            tokenizedCaptions.append(words)

    return tokenizedCaptions

def create_vocab(captions):
    unigrams = {}
    bigrams = {}
    originalCaseWords = {} # unigrams and bigrams with original case preserved
    posTagsBeforeNounDict = {} # dictionary of strings with the part of speech tags
                               # that appear before the noun does in a caption
                               
    (numNoun, numVerb, numTotal) = (0, 0, 0)
    totalAdjs = 0
                               
    for captionWords in captions:

        posTags = nltk.pos_tag(captionWords)
        (nounPresent, verbPresent) = (False, False)
        posTagsBeforeNoun = ''
        allUpper = True
        
        for i in range(len(captionWords)):
            (word, pos) = posTags[i]
            if word.islower():
                allUpper = False
            word = word.lower()
            
            # adds word to vocab or updates count
            if word in unigrams:
                unigrams[word] += 1
            else:
                unigrams[word] = 1
                
            if i != 0: # updates bigram count                    
                if (captionWords[i-1].lower(), word) in bigrams:
                    bigrams[(captionWords[i-1].lower(), word)] += 1
                else:
                    bigrams[(captionWords[i-1].lower(), word)] = 1
            
            if pos[:2] == 'NN':
                nounPresent = True
            elif pos[:2] == 'VB':
                verbPresent = True
            elif pos[:2] == 'JJ':
                totalAdjs += 1

            if not nounPresent: # keeps track of POS tags that appear before a noun does
                posTagsBeforeNoun += ' ' + pos

        if not allUpper: # at least one lowercase word in caption
            for word in captionWords:
                if word in originalCaseWords:
                    originalCaseWords[word] += 1
                else:
                    originalCaseWords[word] = 1
        
        if nounPresent: # if noun does eventually appear in caption...
            # updates count in dictionary for that set of POS tags
            if posTagsBeforeNoun in posTagsBeforeNounDict:
                posTagsBeforeNounDict[posTagsBeforeNoun] += 1
            else:
                posTagsBeforeNounDict[posTagsBeforeNoun] = 1
                                   
        numTotal += 1
        if nounPresent:
            numNoun += 1
        if verbPresent:
            numVerb += 1

    print('% captions with a noun: ' + str(100*numNoun/numTotal))
    print('% captions with a verb: ' + str(100*numVerb/numTotal))
    print('Average # of adjectives per caption: ' + str(totalAdjs/len(captions)))

    return (unigrams, bigrams, originalCaseWords, posTagsBeforeNounDict)

fileIn = open('MS COCO Captions.txt','r')
cocoCaptions = []
for line in fileIn.readlines():
    line = line.replace('\n','')
    cocoCaptions.append(line)
fileIn.close()

cocoTrainingCaptions = cocoCaptions[:400000]
cocoTokenizedCaptions = get_tokens(cocoTrainingCaptions)
(cocoUnigrams, cocoBigrams, cocoWordsWithCase, cocoPOSInfo) = create_vocab(cocoTokenizedCaptions)

fileOut = open('Common COCO Words.txt','w')

# finds and stores most common words in COCO captions
counts = {}
for word in cocoUnigrams.keys():
    if cocoUnigrams[word] in counts:
        counts[cocoUnigrams[word]].append(word)
    else:
        counts[cocoUnigrams[word]] = [word]
        
sortedCounts = sorted(list(counts.keys()), reverse = True)
numWords = 0
for highCount in sortedCounts:
    for word in counts[highCount]:
        if word not in stopWords:
            if numWords < 1500: # POS ignored for first 1500 words
                fileOut.write(word + '\n')
                numWords += 1
            else:
                pos = nltk.pos_tag([word])[0][1]
                if pos[:2] in ["NN","JJ"]:
                    fileOut.write(word + '\n')
                    numWords += 1
    if numWords >= 3500:
        break

fileOut.close()

save_unigrams = open('coco_captions_unigrams.pickle','wb')
pickle.dump(cocoUnigrams, save_unigrams)
save_unigrams.close()

save_bigrams = open('coco_captions_bigrams.pickle','wb')
pickle.dump(cocoBigrams, save_bigrams)
save_bigrams.close()

save_case_info = open('coco_case_info.pickle','wb')
pickle.dump(cocoWordsWithCase, save_case_info)
save_case_info.close()

save_pos_info = open('coco_pos_info.pickle','wb')
pickle.dump(cocoPOSInfo, save_pos_info)
save_pos_info.close()