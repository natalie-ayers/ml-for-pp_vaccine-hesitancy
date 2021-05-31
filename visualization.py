import sys
import os
import time
import functools
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import dates
import json

import dl as DL
import labeling as LABEL

from datetime import datetime
from scipy.interpolate import make_interp_spline
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
#from scipy.interpolate import spline

#from splrep import spline


def plot(df, data, title,fname, y_lim=(-0.8,1.2)):
    '''

    df: dataframe
    data: tuple of x-axis, y-axis, label
    title: title of the plot
    fname: name of the file
    '''
    for pair in data:
        x_col, y_col, label = pair
        x = df[x_col]
        y = df[y_col]
        yhat = savgol_filter(y, 9, 3)
        plt.plot(x,yhat, "-o",label=label)

    plt.legend()
    y_min, y_max = y_lim
    plt.ylim(y_min, y_max)
    plt.draw()
    plt.title(title)
    plt.xticks(rotation=45)
    plt.savefig(fname)
    plt.show()


tweets = pd.DataFrame(columns = ['Date','Count'])
polarity = pd.DataFrame(columns = ['Date','Polarity','positive','negative','compound'])

path = os.getcwd()+'/Data/labeled/'
for f in os.listdir(path):
    try:
        name, indicator = f.split('.')
        date_obj = pd.to_datetime(name.split('_')[0])
    except Exception as e: 
        print(e)
        continue

    with open(path + f) as file_:
        data = pd.DataFrame(json.loads(file_.read())).reset_index()[1:]
        for col in ['positive','negative','compound','score']:
            data[col] = data[col].apply(lambda x: float(x))

        tweets = tweets.append({'Date': date_obj, 'Count':len(data),'Positive':len(data[data['score']==1]),
        'Neutral':len(data[data['score']==0]),'Negative':len(data[data['score']==-1])},ignore_index=True)
        tweets = tweets.sort_values(by='Date') 

        polarity = polarity.append({'Date': date_obj, 'Polarity':data['score'],
                                  'positive':data['positive'], 
                                  'negative':data['negative'],
                                  'compound':data['compound']},ignore_index=True)
        polarity = polarity.sort_values(by='Date') 

print(tweets.head())
print(polarity.head())

for col in ['Count','Polarity','positive','negative','compound']:
    try:
        polarity[col]= polarity[col].apply(lambda x:pd.to_numeric(x,errors='coerce'))
        tweets[col]=tweets[col].apply(lambda x:pd.to_numeric(x,errors='coerce'))
    except:
        pass

# Number of tweet by day
plot(tweets, [('Date','Count','Number of tweets'),('Date','Positive','Number of positive tweets'),
('Date','Neutral','Number of neutral tweets'),('Date','Negative','Number of negative tweets')],
title = 'Number of tweets by day',fname = 'tweets.png', y_lim = (3000,45000))


# Polarity by day
polarity_day = polarity.resample('1D', on = 'Date').agg(
    {'Polarity':'mean', 'positive':'mean', 'negative':'mean', 'compound':'mean'}).reset_index()
polarity_day = polarity_day.dropna(axis=0, how='any')
plot(polarity_day, [('Date','Polarity','Mean Score (1 or 0)'),('Date','positive','Mean Positive'),
              ('Date','negative','Mean Negative'),('Date','compound','Mean Compound Score')], 
              title = 'Polarity by day',fname = 'polarity.png')


# Number of tweet by week
tweets_week = tweets.resample('W', on = 'Date').agg({"Count":'sum','Positive':'sum','Neutral':'sum','Negative':'sum'}).reset_index()
plot(tweets_week, [('Date','Count','Number of tweets'),('Date','Positive','Number of positive tweets'),
    ('Date','Neutral','Number of neutral tweets'),('Date','Negative','Number of negative tweets')],
      title = 'Number of tweets by week',fname = 'tweets_by_week.png', y_lim = (5000,75000))



# Polarity by week
polarity_week = polarity.resample('W', on = 'Date').agg({'Polarity':'mean', 'positive':'mean', 'negative':'mean', 'compound':'mean'}).reset_index()
plot(polarity_week, [('Date','Polarity','Mean Score (1 or 0)'),('Date','positive','Mean Positive'),
              ('Date','negative','Mean Negative'),('Date','compound','Mean Compound Score')], 
              title = 'Polarity by week',fname = 'polarity_by_week.png')

    

