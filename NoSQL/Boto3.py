#!/usr/bin/env python
# coding: utf-8

# In[1]:


import boto3


# In[2]:


# constants
BUCKET_NAME = 'datacont-name-234'
AWS_ACCESS_KEY_ID = 'SOME_ID'
AWS_SECRET_ACCESS_KEY = 'SOME_KEY'


# In[3]:


s3 = boto3.resource('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


# In[4]:


# create bucket
try:
    s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={
    'LocationConstraint': 'us-west-2'}) 
except Exception as e:
    print (e)


# In[5]:


# get bucket
bucket = s3.Bucket(BUCKET_NAME)


# In[6]:


# make bucket publicly readable
bucket.Acl().put(ACL='public-read')


# In[7]:


# upload exp1.csv into the bucket
exp1 = open('exp1.csv', 'rb')
o = s3.Object(BUCKET_NAME, 'exp1.csv').put(Body=exp1)
s3.Object(BUCKET_NAME, 'exp1.csv').Acl().put(ACL='public-read')


# In[8]:


# upload exp2.csv into the bucket
exp2 = open('exp2.csv', 'rb')
o = s3.Object(BUCKET_NAME, 'exp2.csv').put(Body=exp2)
s3.Object(BUCKET_NAME, 'exp2.csv').Acl().put(ACL='public-read')


# In[9]:


# upload exp3.csv into the bucket
exp3 = open('exp3.csv', 'rb')
o = s3.Object(BUCKET_NAME, 'exp3.csv').put(Body=exp3)
s3.Object(BUCKET_NAME, 'exp3.csv').Acl().put(ACL='public-read')


# In[10]:


# create dynamodb table
dyndb = boto3.resource('dynamodb',
    region_name='us-west-2',
    aws_access_key_id=AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


# In[11]:


# create table
try:
    table = dyndb.create_table(
        TableName='DataTable3',
        KeySchema=[
            {
                'AttributeName': 'PartitionKey',
                'KeyType': 'HASH'
            }
            , 
            {
                'AttributeName': 'RowKey',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PartitionKey',
                'AttributeType': 'S'
            }
            , 
            {
                'AttributeName': 'RowKey',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
except Exception as e:
    print (e)
    #if there is an exception, the table may already exist.
    table = dyndb.Table("DataTable")


# In[12]:


# wait for the table to be created
table.meta.client.get_waiter('table_exists').wait(TableName='DataTable3')


# In[13]:


print(table.item_count)


# In[14]:


import csv


# In[15]:


with open('experiments.csv', 'rt') as csvfile: 
    csvf = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(csvf)
    for item in csvf:
        print(item)
        body = open(item[4], 'rb') 
        s3.Object(BUCKET_NAME, item[4]).put(Body=body) 
        md = s3.Object(BUCKET_NAME, item[4]).Acl().put(ACL='public-read')
        
        url = " https://s3-us-west-2.amazonaws.com/"+BUCKET_NAME+"/"+item[4] 
        metadata_item = {'PartitionKey': item[0], 'RowKey': item[1],
            'Conductivity' : item[2], 'Concentration' : item[3], 'url':url} # 'RowKey': item[1]
        try: 
            table.put_item(Item=metadata_item)
        except:
            print("item may already be there or another failure")


# In[17]:


response = table.get_item(
    Key={
        'PartitionKey': '1',
        'RowKey': '-1'
    }
)
item = response['Item'] 
print(item)


# In[19]:


print(response)


# In[ ]:




