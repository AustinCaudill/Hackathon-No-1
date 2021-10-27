""" 

Austin Caudill


Questions to be answered:
What affects open %?​
    Send time, day of week, word count, link count ​
Link sheets No-SQL database​
What link is the most popular?​
What topic is most popular?​
What drives link clicks? ​
How do ads affect?
 """

# Load Imports
import os
import pandas as pd
from autoviz.AutoViz_Class import AutoViz_Class
import urllib3
import certifi
import validators
from bs4 import BeautifulSoup

import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# Load Data
email_summary = pd.read_excel(r'summary.xlsx', parse_dates=[0])
email_summary['Date'] = email_summary['Date/Time'].dt.date
email_summary['Time'] = email_summary['Date/Time'].dt.time
email_summary['Hour'] = email_summary['Date/Time'].dt.hour
email_summary['Day'] = email_summary['Date/Time'].dt.day_name()

files = os.listdir('link_data')
link_data = pd.DataFrame() # Initialize dataframe
for f in files:
    data = pd.read_excel('./link_data/'+f, 'Sheet1')
    link_data = link_data.append(data)

# Need to cleanup by removing rows with "nan"
link_data = link_data.dropna()

bad_URLS = 0
result = []
# Need to remove bad URLs
for l in link_data['Link']:
    try:
        test = validators.url(l)
        print(test)
        result.append(test)
    except:
        result.append("FAILED")

link_data['Result'] = result
cleaned_URLs = link_data.loc[link_data['Result'] == True]
cleaned_URLs = cleaned_URLs[~cleaned_URLs.Link.str.contains('pdf|jpg')]

cleaned_URLs = cleaned_URLs.loc[cleaned_URLs['Clicks'] > 20]



# Perform EDA

""" AV = AutoViz_Class()
filename = "" # Not Needed
dft = AV.AutoViz(
    filename,
    sep=",",
    depVar="Open Rate", # Target Variable
    dfte=email_summary,
    header=0,
    verbose=1,
    lowess=True,
    chart_format="svg",
) """


# Time to scrape link data
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
soupey = []
for link in cleaned_URLs['Link']:
    try:
        print("Getting:", link)
        req = http.request('GET', link, headers=headers, retries=urllib3.Retry(redirect=2, raise_on_redirect=False))
        if req.status != 200: 
            continue
        soup = BeautifulSoup(req.data, "html.parser")
        text = soup.get_text()
        print(text)
        soupey.append(text)
    except:
        print('failed')
        continue


# Text Preprocessing
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
stop_words = set(stopwords.words('english'))
stop_words_ext = ['n', 'please', 'nthe', 'license', 'cc', 'nmore', 'xa', 'c', 'u', 'r', 'f', 'licensing','licensed', 'licenses', 'creative commons','used','copyright'] # custom word exclusion list.


def preprocess(text):
    
    #regular expression keeping only letters - more on them later
    letters_only_text = re.sub("[^a-zA-Z]", " ", text)
    letters_only_text  = re.sub("'", "", letters_only_text)

    # convert to lower case and split into words -> convert string into list ( 'hello world' -> ['hello', 'world'])
    words = letters_only_text.lower().split()

    cleaned_words = []
    
    # remove stopwords
    for word in words:
        if word not in stop_words and word not in stop_words_ext:
            cleaned_words.append(word)
            
    cleaned_words = [i.replace("'", "") for i in cleaned_words]      

    return cleaned_words

soupey = str(soupey)
cleaned_soupey = preprocess(soupey)    

word_tokens = word_tokenize(str(cleaned_soupey)) #converts into individual words

number_of_words = len(word_tokens)
print(number_of_words)

from wordcloud import WordCloud
import matplotlib.pyplot as plt

wordcloud = WordCloud(width = 700, height = 700, background_color ='white', min_font_size = 10).generate(str(word_tokens) )
  
# plot the WordCloud image                        
plt.figure(figsize = (10, 10), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()
plt.savefig('test.png')

print("finished")