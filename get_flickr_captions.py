from flickrapi import FlickrAPI
from pprint import pprint
from nltk.tokenize import sent_tokenize
import time
import pickle

flickr_public = "MY_PUBLIC_KEY"
flickr_secret = "MY_SECRET_KEY"

def get_flickr_captions(n, keywords):

    captions = {}
    start_time = time.time()

    for i in range(n):
        
        for j in range(len(keywords)):
            # obtains (up to 500) photos with corresponding tag in keywords
            taggedPhotos = flickr.photos.search(extras=['description'],
                                          page=i+1,
                                          per_page=500,
                                          tags=[keywords[j]])['photos']['photo']

            # obtains (up to 500) recent photos
            recentPhotos = flickr.photos.getRecent(extras=['description'],
                                             page=len(keywords)*i + j+1,
                                             per_page=500)['photos']['photo']
            
            for photo in (taggedPhotos + recentPhotos):
                # both 'title' and 'description' could contain a caption
                (title, description) = (photo['title'], photo['description']['_content'])
                # splits captions into sentences
                photoCaptions = sent_tokenize(title) + sent_tokenize(description)
                for caption in photoCaptions:
                    if caption not in captions: # if new, adds caption and photo id
                        captions[caption] = photo['id']

        print('# of Captions Retrieved: ' + str(len(list(captions.keys()))))
        print('Time Spent (seconds): ' + str(time.time() - start_time))

    captions.pop('',None) # removes empty caption
    return captions

# retrieves list of MS COCO category names
fileIn = open('COCO Categories.txt','r')
cocoCategories = []
for line in fileIn.readlines():
    if line[-1] == '\n':
        line = line[:-1]
    cocoCategories.append(line)
fileIn.close()

flickr = FlickrAPI(flickr_public, flickr_secret, format='parsed-json')

captions_f = open('captions_dict.pickle','rb')
captions = pickle.load(captions_f)
captions_f.close()

newCaptions = get_flickr_captions(20, cocoCategories)
captions.update(newCaptions)

# stores captions
save_captions = open('captions_dict.pickle','wb')
pickle.dump(captions, save_captions)
save_captions.close()
