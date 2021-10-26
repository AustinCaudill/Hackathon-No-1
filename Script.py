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
link_data.loc[link_data['Result'] == True]



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
for link in link_data['Link']:
    print("Getting:", link)
    r2 = http.request('GET', link, headers=headers, retries=urllib3.Retry(redirect=2, raise_on_redirect=False))
    if r2.status != 200: 
     continue
    soup2 = BeautifulSoup(r2.read(), "html.parser")