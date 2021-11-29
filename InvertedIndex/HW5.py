#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys, shutil
from pyspark import SparkContext, SparkConf
from pyspark.sql.functions import input_file_name
import zipfile, tarfile
import os
import re
from string import punctuation
# regex to split by punctuation
r = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))
stopwords = ['they', 'she', 'he', 'it', 'the', 'as', 'is', 'and']


# In[2]:


# unzip Data.zip and .tar.gz files
with zipfile.ZipFile('Data.zip', 'r') as zip_ref:
    zip_ref.extractall('.')
file = tarfile.open('Data/Hugo.tar.gz')
file.extractall('Data/')
file.close()
file = tarfile.open('Data/shakespeare.tar.gz')
file.extractall('Data/')
file.close()
file = tarfile.open('Data/Tolstoy.tar.gz')
file.extractall('Data/')
file.close()


# In[3]:


# traverse Data directory, move files to the input folder
for root, dirs, files in os.walk("Data"):
    path = root.split(os.sep)
    for file in files:
        if (not file.endswith('.tar.gz')) and (not file.endswith('.zip')):
            shutil.move(root + '/' +file, 'input/')


# In[4]:


# word to posting mapper
def word_posting_mapper(pair):
    # split by punctuation
    words = r.split(pair[1])
    # turn to lower case
    words = list(map(lambda w: w.lower(), words))
    # remove stopwords
    words = filter(lambda w: w not in stopwords and w != "", words)
    # return list of word-posting tuples
    # posting is in dictionary format, with filename as key and count (1) as value
    return [(word, {pair[0]: 1}) for word in list(words)] 


# In[5]:


# reducer
def reducer(a,b):
    # merge posting dictionary by key, i.e. for each word, sum the word counts for each filename
    return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}


# In[6]:


conf = SparkConf()
# create Spark context with necessary configuration
sc = SparkContext.getOrCreate(conf=conf)
# Conduct MapReduce and write the output to folder
wordCounts = sc.textFile("input")
# get the filename, filecontent tuple
path = sc.wholeTextFiles('input').map(
    lambda x : (x[0], x[1])
)
words = path.flatMap(word_posting_mapper) 
reduced = words.reduceByKey(reducer) 
# reduce and outtput 1 file
reduced.coalesce(1).saveAsTextFile("output")
