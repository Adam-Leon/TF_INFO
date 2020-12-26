#!/usr/bin/env python
# coding: utf-8

# In[1]:


# coding=UTF-8
import requests
import json
import csv 
from _ast import NotIn, If
import time
import pandas as pd

#FHIR 欄位資料查詢 http://hl7.org/fhir/
#Spark FHIR API 查詢http ://120.126.47.179:5555/swagger/index.html


#病人資料
url = 'http://120.126.47.179:5555/fhir/QuestionnaireResponse/'
datalist = []
for i in  range(3,103):
    
    headers = {'Content-Type': 'application/json'}
    data = requests.request("GET" ,url+str(i)+'/' ,headers=headers)
    #print(data.text)

    datajson = json.loads(data.text)
    id = datajson['id']
    print('取得資料 GET '+id)
    row = { 'id':id }
    for item in datajson['item'] :
        q = item['item'][0]['text']
        a = list(item['item'][0]['answer'][0].values())[0]
        row[q] = str(a)
        print( q + ' ' + str(a))
    datalist.append(row)
# print(datalist)


df= pd.DataFrame(datalist)
print(df)


# In[2]:


#這串是實驗是否能在執行時抓到本程式的檔名
import sys
# importing os module for absolute path
import os
# printing the script name
# first element of sys.argv list
print(os.path.basename(sys.argv[0]))


# In[9]:


#這串就是單純地對(df)這個dataframe做清理
def cleaning(df):

    #select the desired columns
    df['age']=pd.to_numeric(df['年齡:'])
    df['bmi']=pd.to_numeric(df['請計算您的身體質量指數(BMI):'])
    df['ssr']=pd.to_numeric(df['請問您的右手收縮壓為:'])
    df[['gender','diebetes','hyperlipidemia','drink','risk']]=df[['性別:','是否曾有糖尿病?','是否曾有高血脂?','是否有喝酒的習慣?','評估結果:']]
    df=df[['id','age','gender','diebetes','hyperlipidemia','drink','bmi','ssr','risk']]
    #cleaning each column
    #for numeric data, value out of selected range would be set as -999, null stays null
    #for categorical data, value out of options, including null, would be labeled as Z
    
    #age
    for i in range(len(df)):
        if df.loc[i,'age'] <0 or df.loc[i,'age'] >100:
            df.loc[i,'age']=-999
    
    #gender to category
    for i in range(len(df)):
        if df.loc[i,'gender'] not in ['female','male'] and bool(df.loc[i,'gender'])==True:
            df.loc[i,'gender']='Z'

    #g_bmi to float with one decimal
    for i in range(len(df)):
        if df.loc[i,'bmi'] <0 or df.loc[i,'bmi'] >50:
            df.loc[i,'bmi']=-999
    df.loc[:,'bmi']=df.loc[:,'bmi'].round(1)
    
    #g_ssr to float with one decimal
    for i in range(len(df)):
        if df.loc[i,'ssr'] <60 or df.loc[i,'ssr'] >300:
            df.loc[i,'ssr']=-999
    df.loc[:,'ssr']=df.loc[:,'ssr'].round(1)

    #mdrug07 to category
    for i in range(len(df)):
        if df.loc[i,'risk'] not in ['low','medium','high'] and bool(df.loc[i,'risk'])+1==True:
            df.loc[i,'risk']='Z'
   
    return df


# In[10]:


#release note的內容，.format是對{}的內容做指定
def release_note(path,csvname,df):
    #如果抓到的程式名稱是錯的，就把{name}對應的元素改掉
    Info="""
    {csvname} is cleaned on {time}, by {name}\n
    The data was downloaded from {resource}, including {rows} samples(rows).\n
    {columns} variants(columns) had been selected and cleaned.\n
    
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n
    
    All null values were kept null.\n
    For numeric data, values out of selected range were set to -999.\n
    For categorical data, values out of selected categories were labeled as Z.\n
    
    "id" representing "user id" was kept.\n
    "age" representing "patient age" was treated as numeric data, 0 < age <= 100.\n
    "gender" representing "patient gender" was treated as categorical data,  either male or female.\n
    
    "diebetes" representing "Have you been diagnosed with diabetes?" was treated as categorical data, either False or True.\n
    "hyperlipidemia" representing "Have you been diagnosed with hyperlipidemia drugs" was treated as categorical data, either False or True.\n
    "drink" representing "Do you drink regularly" was treated as categorical data, either False or True.\n

    "g_bmi" representing "patient bmi" was treated as numeric data, 0 < g_bmi <= 50.\n
    "g_ssr" representing "right hand systolic blood pressure" was treated as numeric data, 60 < g_ssr <= 300.\n
     
    "risk" representing "evaluated risk of having stroke" was treated as categorical data, low, middle or high\n
    
    """.format(csvname=csvname, name=os.path.basename(sys.argv[0]), resource='FHIR R01-001', time=time.asctime(time.localtime()), rows=len(df), columns=len(df.columns))
    f=open(path+"release_note.txt", "w")
    f.write(Info)
    f.close()


# In[11]:


#codebook的內容，.format是對{}的內容做指定
def codebook(path,csvname,df):
    Info="""
    {csvname} is cleaned on {time}, by {name}\n
    The data was downloaded from {resource}, including {rows} samples(rows).\n
    {columns} variants(columns) had been selected and cleaned.\n
    
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n
    
    All null values were kept null.\n
    For numeric data, values out of selected range were set to -999.\n
    For categorical data, values out of selected categories were labeled as Z.\n
    
    "id" representing "user id" was kept.\n
    "age" representing "patient age" was treated as numeric data, 0 < age <= 100.\n
    "gender" representing "patient gender" was treated as categorical data,  either male or female.\n
    
    "diebetes" representing "Have you been diagnosed with diabetes?" was treated as categorical data, either False or True.\n
    "hyperlipidemia" representing "Have you been diagnosed with hyperlipidemia drugs" was treated as categorical data, either False or True.\n
    "drink" representing "Do you drink regularly" was treated as categorical data, either False or True.\n

    "g_bmi" representing "patient bmi" was treated as numeric data, 0 < g_bmi <= 50.\n
    "g_ssr" representing "right hand systolic blood pressure" was treated as numeric data, 60 < g_ssr <= 300.\n
     
    "risk" representing "evaluated risk of having stroke" was treated as categorical data, low, middle or high\n
    
    """.format(csvname=csvname, name=os.path.basename(sys.argv[0]),resource='FHIR R01-001', time=time.asctime(time.localtime()), rows=len(df), columns=len(df.columns))
    f=open(path+"codebook.txt", "w")
    f.write(Info)
    f.close()


# In[12]:


path1='C:/Users/Adam/Desktop/GIT_Final/'
path2='C:/Users/Adam/Documents/FTP/Read/'
csvname='R01001_'+str(time.localtime()[0])+str(time.localtime()[1])+str(time.localtime()[2])+'_v1'+'.csv'


# In[13]:


#dataframe變成清理過的dataframe
df=cleaning(df)
#把df存到path1和path2，並存成名為filename的csv檔
df.to_csv(path1+csvname)
df.to_csv(path2+csvname)
#把release_note存在path1和2
release_note(path1,csvname,df)
release_note(path2,csvname,df)
#把codebook存在path1和2
codebook(path1,csvname,df)
codebook(path2,csvname,df)


# In[17]:


#shutil.copy(執行中的程式, 指定路徑+取檔名(目前執行的程式))
import shutil
shutil.copy(sys.argv[0], path1+os.path.basename(sys.argv[0])) 
shutil.copy(sys.argv[0], path2+os.path.basename(sys.argv[0]))


# In[ ]:





# In[ ]:




