import nltk
from nltk.corpus import words
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle
import string
import spacy
nlp = spacy.load('en')

def is_english_word(word, pos):
    englishWord = False
    if word in englishWords:
        englishWord = True
    else: # check if lemmatized word is in dictionary
        if pos[:2] in tagConversions:
            newPOSTag = tagConversions[pos[:2]]
            newWord = lemmatizer.lemmatize(word, pos=newPOSTag)
            if newWord in englishWords:
                englishWord = True   
                
    return englishWord

def reconstruct_caption(words):
    '''Reconstructs a caption based on the words provided.'''
    caption = ""
    for i in range(len(words)):
        if i != 0 and (words[i] not in string.punctuation or words[i] == "-"):
            caption += " "
        caption += words[i]
    
    return caption

def remove_uppercase_words(words):
    '''Checks for and modifies words with unusual capitalization (ex. all uppercase).'''
    for i in range(len(words)):
        word = words[i]
        if not word.islower() and not word.istitle() and word.lower() in cocoVocab:
            # if capitalization is uncommon...
            if word in cocoWordsWithCase and cocoWordsWithCase[word]/cocoVocab[word.lower()] < 0.20:
                words[i] = word[0] + word[1:].lower()
            elif word not in cocoWordsWithCase and cocoVocab[word.lower()] >= 10:
                words[i] = word[0] + word[1:].lower()
                
    return words
    
def remove_proper_nouns(caption):
    '''Returns a list of a caption's words with proper nouns removed, or None if no changes are necessary.'''
    allowedEnts = {"NORP","LANGUAGE","DATE","TIME","QUANTITY","ORDINAL","CARDINAL"}
    doc = nlp(caption)
    ents = []
    for ent in doc.ents:
        if ent.label_ in allowedEnts:
            continue
        
        entWords = ent.text.split(' ')
        namedEntity = False

        for word in entWords:
            if not word.islower():
                if word.lower() in cocoWordsWithCase:
                    # if word is typically/only seen in lowercase...
                    if word in cocoWordsWithCase and cocoWordsWithCase[word]/cocoWordsWithCase[word.lower()] < 0.20:
                        continue
                    elif word not in cocoWordsWithCase and cocoWordsWithCase[word.lower()] >= 5:
                        continue
                namedEntity = True # True if any word in NE is often capitalized
                break
            
        if namedEntity:
            ents.append(ent)
            
    neIndices = set([]) # indices of words that are part of NE phrase
    phraseDefiningDeps = {"prep","dobj","compound","appos"} # dependencies that allow the extraction of a phrase

    for ent in ents:
        neRoot = None
        current = ent.root
        
        while current.dep_ != "ROOT" and current.dep_ != "nsubj":
            if current.dep_ in phraseDefiningDeps: # extraction point found
                neRoot = current
                break
            current = current.head
        
        if neRoot != None:
            for i in range(neRoot.left_edge.i, neRoot.right_edge.i + 1):
                neIndices.add(i)

            currentChar = 0
            for i in range(len(doc)): # ensures entire NE is removed
                if currentChar >= ent.start_char and currentChar + len(doc[i].text) <= ent.end_char:
                    neIndices.add(i)
                currentChar += len(doc[i].text) + 1

    if len(ents) == 0:
        newWords = None
    else:
        newWords = [] # remaining words
        for i in range(len(doc)):
            if i not in neIndices:
                newWords.append(doc[i].text)
    
    return newWords

coco_vocab_f = open('coco_captions_unigrams.pickle','rb')
cocoVocab = pickle.load(coco_vocab_f) # dictionary with frequencies of COCO unigrams
coco_vocab_f.close()

numCOCOWords = 0
for word in cocoVocab.keys():
    numCOCOWords += cocoVocab[word]
    
coco_bigrams_f = open('coco_captions_bigrams.pickle','rb')
cocoBigrams = pickle.load(coco_bigrams_f)
coco_bigrams_f.close()

coco_case_info_f = open('coco_case_info.pickle','rb')
cocoWordsWithCase = pickle.load(coco_case_info_f) # frequencies of words with original case
coco_case_info_f.close()

coco_pos_info_f = open('coco_pos_info.pickle','rb')
cocoPOSInfo = pickle.load(coco_pos_info_f) # dictionary with sets of POS tags that
coco_vocab_f.close()                       # appear before a noun in COCO captions

numCOCOCaptions = 0 # number of COCO captions with a noun 
for posTagSet in cocoPOSInfo.keys():
    numCOCOCaptions += cocoPOSInfo[posTagSet]

captions_f = open('captions_dict.pickle','rb')
captionsDict = pickle.load(captions_f)
captions_f.close()
captions = list(captionsDict.keys())

fileIn = open('MS COCO Captions.txt','r')
cocoCaptions = []
for line in fileIn.readlines():
    line = line.replace('\n','')
    cocoCaptions.append(line)
cocoTestingCaptions = cocoCaptions[400000:] # ~15000 testing captions
cocoCaptionsSet = set(cocoTestingCaptions)
    
englishWords = set(words.words())
tagConversions = {'NN':wordnet.NOUN,'VB':wordnet.VERB,'JJ':wordnet.ADJ,'RB':wordnet.ADV}
allowedChars = " ...!?,':;-" # allowed characters (besides alphabetic ones)
# undesired personal/possessive pronouns
penalizedPRPs = set(['us','we','ourselves','ours','you','my','yourself','your','our','myself','i','me'])

stopWords = []
for word in stopwords.words('english'):
    pos = nltk.pos_tag([word])[0][1]
    if pos[:2] not in ['NN','PR']:
        stopWords.append(word)
stopWords = set(stopWords)

captionProbs = {}
for length in range(4,11):
    captionProbs[length] = {} # captions will be separated by length

for caption in captions:
    
    properCaption = True
    for char in caption:
        if not char.isalpha() and char not in allowedChars:
            properCaption = False
            break

    if properCaption: # if caption only contains allowed characters...
        words = word_tokenize(caption) 
        words = remove_uppercase_words(words)
        modifiedCap = reconstruct_caption(words)
        newCaptionWords = remove_proper_nouns(modifiedCap)
        
        if newCaptionWords != None: # caption contained NE
            words = newCaptionWords
            newCaption = reconstruct_caption(words)
            captionsDict[newCaption] = captionsDict[caption]
            caption = newCaption

        probability = 1
        # makes all letters lowercase
        for i in range(len(words)):
            if not words[i].islower() and i != 0:
                probability *= 1/10 # penalizes capitalized words
            words[i] = words[i].lower()
            
        posTags = nltk.pos_tag(words)
        numWords = 0 # number of unique words
        for word in list(set(words)):
            if word not in allowedChars and word not in stopWords:
                numWords += 1

        if numWords >= 4 and numWords <= 10:
            (nounFound, verbFound) = (False, False)
            numAdj = 0
            posTagsBeforeNoun = ''
            
            # adjusts probability based on words in caption
            for i in range(len(words)):
                (word, pos) = (words[i],posTags[i][1])
                
                if word not in allowedChars:
                    if word not in stopWords:
                        if word in penalizedPRPs: # penalizes undesired pronouns
                            probability *= 1/(numCOCOWords**3+1)
                        elif i != 0 and (words[i-1], word) in cocoBigrams: # bigram check
                            probability *= cocoBigrams[(words[i-1], word)]/cocoVocab[words[i-1]]
                        elif word in cocoVocab: # unigram check
                            probability *= cocoVocab[word]/numCOCOWords
                        else: # unknown word
                            if is_english_word(word, pos):
                                probability *= 1/(numCOCOWords+1)
                            else: # penalizes non-English words
                                probability *= 1/(numCOCOWords**2+1)

                    if pos[:2] == 'JJ':
                        numAdj += 1
                    elif pos[:2] == 'VB':
                        verbFound = True
                    elif pos[:2] == 'NN':
                        nounFound = True
                    if not nounFound:
                        posTagsBeforeNoun += ' ' + pos

            # adjusts probability based on POS tags in caption
            probability *= 10**(min(numAdj, numWords/3))
            if not verbFound:
                probability *= 1/10
            if not nounFound:
                probability *= (1/(numCOCOCaptions+1))**(2*numWords/5)
            else: # noun in caption
                if posTagsBeforeNoun[:3] == ' VB': # caption starting with verb
                    probability *= (1/(numCOCOCaptions+1))**(numWords/5)
                    
                if posTagsBeforeNoun in cocoPOSInfo:
                    probability *= (cocoPOSInfo[posTagsBeforeNoun]/numCOCOCaptions)**(numWords/10)
                else:
                    probability *= (1/(numCOCOCaptions+1))**(numWords/10)
            
            # adds caption to dictionary based on number of words
            if probability in captionProbs[numWords]:
                captionProbs[numWords][probability].append(caption)
            else:
                captionProbs[numWords][probability] = [caption]

fileOut = open('Flickr Captions.txt','w')
numCaptions = {4:4375, 5:7000, 6:11250, 7:10500, 8:9000, 9:4750, 10:3125}
photoIDs = []

for capLength in range(4,11):

    fileOut.write(f'\n\nCaptions with {capLength} words')
    fileOut.write('\n---------')
    rank = 0

    probs = sorted(list(captionProbs[capLength].keys()), reverse=True) # probabilities from highest to lowest
    for highProb in probs[:numCaptions[capLength]]:
        for caption in captionProbs[capLength][highProb]:
            photoIDs.append(captionsDict[caption])
            rank += 1
            fileOut.write(f'\n{rank} ' + str(caption.encode('utf-8'))[2:-1])

fileOut.close()

# stores photo IDs of high-scoring captions
save_ids = open('caption_ids.pickle','wb')
pickle.dump(photoIDs, save_ids)
save_ids.close()
