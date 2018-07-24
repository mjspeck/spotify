import pandas as pd
import numpy as np
import re
import pickle
from datetime import datetime as dt

from tqdm import tqdm
import spotipy
import spotipy.util as util

from keys import *
from randomfunctions import print_cols

scope = 'user-library-read'

token = util.prompt_for_user_token(username,
                           scope,
                           client_id=client_id,
                           client_secret=client_secret,
                           redirect_uri=redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
    total_tracks = sp.current_user_saved_tracks()['total']
else:
    print("Can't get token for", username)
    
def get_tracks(num_tracks):
    max_ = 50 * int(num_tracks / 50) + 50
    tracks = []
    for i in tqdm(range(0, max_, 50), desc='Progress'):
        results = sp.current_user_saved_tracks(offset=i, limit=50)
        for j in results['items']:
            tracks.append(j['track'])
                   
    return tracks

tracks = get_tracks(total_tracks)
track_df = pd.DataFrame(tracks)

def get_audio_tracks(ids):
    num_tracks = len(ids)
    max_ = 50 * int(num_tracks / 50) + 50
    
    audio_info = []   
    for i in tqdm(range(0, max_, 50), desc='Progress'):
        if i == max_:
            results = sp.audio_features(tracks=ids[i:])
            audio_info += results
            
        else:
            results = sp.audio_features(tracks=ids[i:i+50])
            audio_info += results
            
    return audio_info

ids = track_df['id']
audio_features = get_audio_tracks(ids)

audio_df = pd.DataFrame(audio_features)
final_df = pd.concat([audio_df, track_df], axis=1)

time = dt.now()

pickle.dump(final_df, open(f'../assets/pickles/data_{time}.pickle', 'wb'))