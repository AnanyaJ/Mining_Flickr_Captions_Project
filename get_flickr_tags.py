from flickrapi import FlickrAPI
import pickle

def find_most_common(dictionary, n, fileName):
    '''Finds and stores the keys with the n highest values in a dictionary.'''
    counts = {}
    for key in dictionary:
        if dictionary[key] in counts:
            counts[dictionary[key]].append(key)
        else:
            counts[dictionary[key]] = [key]

    fileOut = open(fileName,'w')

    sortedCounts = sorted(list(counts.keys()), reverse=True)
    for highCount in sortedCounts[:n]:
        for key in counts[highCount]:
            fileOut.write(str(key.encode('utf-8'))[2:-1] + '\n')

    fileOut.close()   

flickr_public = "MY_PUBLIC_KEY"
flickr_secret = "MY_SECRET_KEY"
flickr = FlickrAPI(flickr_public, flickr_secret, format='parsed-json')

# photo IDs of 3600 highest-scoring Flickr captions
caption_ids_f = open('caption_ids.pickle','rb')
captionIDs = pickle.load(caption_ids_f)[:3600]
caption_ids_f.close()

tagsDict = {} # number of times each tag appears
authorsDict = {} # number of times each author appears

for photoID in captionIDs:
    try:
        photoInfo = flickr.photos.getInfo(photo_id=photoID)['photo']
        tags = [tag['_content'] for tag in photoInfo['tags']['tag']]
        for tag in tags: # updates count for tag in dictionary
            if tag in tagsDict:
                tagsDict[tag] += 1
            else:
                tagsDict[tag] = 1
                
        authorID = photoInfo['owner']['nsid']
        if authorID in authorsDict: # updates count for author ID
            authorsDict[authorID] += 1
        else:
            authorsDict[authorID] = 1
            
    except:
        print('Photo not found. ID: ' + photoID)

find_most_common(tagsDict, 100, 'Common Flickr Tags.txt')
find_most_common(authorsDict, 15, 'Common Flickr Authors.txt')
