from flickrapi import FlickrAPI
from urllib.request import urlretrieve
from pprint import pprint
import os, time, sys
import json

key = '61c40bbd25de94fcdb17c4c180e14ab2'
secret = '903a33c5f578e995'
wait_time = 0.1

# read config
with open('animalai.conf', 'r') as f:
    settings = json.load(f)

flickr = FlickrAPI(key, secret, format='parsed-json')

for animalname in settings['classes']:
    # save folder
    savedir = './images/' + animalname

    result = flickr.photos.search(
        text = animalname,
        per_page = 400,
        media = 'photos',
        sort = 'relevance',
        safe_search = 1,
        extras = 'url_q, licence'
    )

    photos = result['photos']

    for i, photo in enumerate(photos['photo']):
        url_q = photo['url_q']
        filepath = savedir + '/' + photo['id'] + '.jpg'
        if os.path.exists(filepath): continue
        urlretrieve(url_q, filepath)
        print(filepath + ' retrieved')
        time.sleep(wait_time)

