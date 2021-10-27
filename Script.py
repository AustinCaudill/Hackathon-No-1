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
from nltk import ngrams
from collections import Counter
import seaborn as sns
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
# Used to make plots appear in window.
%matplotlib inline
import matplotlib.pyplot as plt



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
cleaned_URLs = cleaned_URLs[~cleaned_URLs.Link.str.contains('pdf|jpg|jpeg|JPG|png|cgi')]

cleaned_URLs = cleaned_URLs.loc[cleaned_URLs['Clicks'] > 80]


# Perform EDA

AV = AutoViz_Class()
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
)


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
stop_words = set(stopwords.words('english'))
stop_words_ext = ['http','n', 'please', 'nthe', 'license', 'cc', 'nmore', 'xa', 'c', 'u', 'r', 'f', 'licensing','licensed', 'licenses', 'creative commons','used','copyright'] # custom word exclusion list.

def preprocess(text):

    new_tokens = word_tokenize(text)
    new_tokens = [t for t in new_tokens if t.isalpha()]
    new_tokens = [t.lower() for t in new_tokens]

    lemmatizer = WordNetLemmatizer()
    new_tokens =[lemmatizer.lemmatize(t) for t in new_tokens]

    cleaned_words = []
    # remove stopwords
    for word in new_tokens:
        if word not in stop_words and word not in stop_words_ext:
            cleaned_words.append(word)
    
    #counts the words, pairs and trigrams
    counted = Counter(cleaned_words)
    counted_2= Counter(ngrams(cleaned_words,2))
    counted_3= Counter(ngrams(cleaned_words,3))
    #creates 3 data frames and returns thems
    word_freq = pd.DataFrame(counted.items(),columns=['word','frequency']).sort_values(by='frequency',ascending=False)
    word_pairs =pd.DataFrame(counted_2.items(),columns=['pairs','frequency']).sort_values(by='frequency',ascending=False)
    trigrams =pd.DataFrame(counted_3.items(),columns=['trigrams','frequency']).sort_values(by='frequency',ascending=False)

    return cleaned_words,word_freq,word_pairs,trigrams

soupey = str(soupey)
cleaned_soupey,word_freq,word_pairs,trigrams = preprocess(soupey)    

number_of_words = len(cleaned_soupey)
print(number_of_words)


cleaned_soupey = " ".join(cleaned_soupey)
wordcloud = WordCloud(width = 700, height = 700, background_color ='white', min_font_size = 10).generate((cleaned_soupey))
  
# plot the WordCloud image                        
plt.figure(figsize = (10, 10), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()


# create subplot of the different data frames
fig, axes = plt.subplots(3,1,figsize=(8,20))
sns.barplot(ax=axes[0],x='frequency',y='word',data=word_freq.head(30))
sns.barplot(ax=axes[1],x='frequency',y='pairs',data=word_pairs.head(30))
sns.barplot(ax=axes[2],x='frequency',y='trigrams',data=trigrams.head(30))




print("Script Finished")
