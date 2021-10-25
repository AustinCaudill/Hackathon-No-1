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
import pandas as pd
from autoviz.AutoViz_Class import AutoViz_Class

email_summary = pd.read_excel(r'summary.xlsx')
email_summary['Date'] = email_summary['Date/Time'].dt.date
email_summary['Time'] = email_summary['Date/Time'].dt.time

# Perform EDA
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