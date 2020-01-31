import spacy
nlp = spacy.load('en')
            # "Fire Hydrant on Filbert Street Steps, San Francisco"
            # "She passed the ball to John."
            # "View from the train on the East Coast line between Edinburgh and York"
sentence = "A man throwing a ball for his dog at Broadhaven south."
doc = nlp(sentence)

neIndices = set([]) # indices of words that are part of an NE phrase

for ent in doc.ents:
    if ent.root.dep_ != "nsubj":
        current = ent.root
        neRoot = None # root of subtree with NE
        while True:
            if current.dep_ == "ROOT": # reached root of tree
                break
            elif current.head.text.lower() == "in":
                neRoot = current.head
                break
            elif neRoot == None and current.dep_ == "pobj":
                neRoot = current.head
            current = current.head
            
        if neRoot == None:
            neRoot = ent.root.head
        
        for i in range(neRoot.left_edge.i, neRoot.right_edge.i + 1):
            neIndices.add(i)
        
# reconstructs caption
newCaption = ""
for i in range(len(doc)):
    if i not in neIndices:
        newCaption += doc[i].text + " "

print(newCaption)
    
        
    
        
        
            
    