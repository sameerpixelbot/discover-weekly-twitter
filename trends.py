#this file is used to detect trends in cluster
import pymongo
import datetime
import pandas as pd
from sklearn.cluster import DBSCAN

pd.set_option('display.max_colwidth',-1)

#connecting to mongodb
client=pymongo.MongoClient()
db=client.twitter

#setting Dates
today=datetime.date.today()
seven_days_back=today - datetime.timedelta(days=7)

#taking desicion to view or not
desicion=input('If you want to see trends press 1 else 0 : ')

while(desicion=='1'):
    
    cluster_no=int(input('Enter the cluster no : '))
    
    #getting users###########################################################
    users=[]
    for user in db.users.find({'cluster_number':cluster_no}):
        print(user['user']['screen_name'])
        users.append(user)
    
    #getting tweets#########################################################'
    print()
    print('Collecting tweets')
    tweets=[]
    for user in users:
        if seven_days_back.year==today.year :
    
            for tweet in db.tweets.find({'$and':[{'user.id':user['user']['id']},
                                         {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]},
                                         {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}):
                tweets.append(tweet)

        else:
    
            for tweet in db.tweets.find({'$and':[{'user.id':user['user']['id']},
                                         {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]}]}):
                tweets.append(tweet)
            for tweet in db.tweets.find({'$and':[{'user.id':user['user']['id']},
                                         {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}]}):
                tweets.append(tweet)

    print(len(tweets),' tweets in past 7 days without removing duplicates')
    
    #removing duplicate tweets################################################
    ids={}
    duplicates=[]
    index=0

    for tweet in tweets:
    
        if tweet['id'] in ids:
            duplicates.append(index)
        else:
            ids[tweet['id']]=0
    
        index+=1
    
    for index in sorted(duplicates,reverse=True):
        del tweets[index]
    
    print(len(tweets),' Size after removing duplicates')
    
    #making vector templet to cluster tweets to get threads###########
    print('Feature Engineering')
    directed={}
    days=[]

    for tweet in tweets:
    
        if tweet['created_day'] not in days:
            days.append(tweet['created_day'])
        
        for member in tweet['entities']['user_mentions']:
            if member['screen_name'] not in directed:
                directed[member['screen_name']]=1
        
        if tweet['user']['screen_name'] in directed:
            directed.pop(tweet['user']['screen_name'])
    
        if 'quoted_status' in tweet:
        
            for member in tweet['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            for member in tweet['quoted_status']['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            if tweet['quoted_status']['user']['screen_name'] not in directed:
                directed[tweet['quoted_status']['user']['screen_name']]=1
        
            if tweet['user']['screen_name'] in directed:
                directed.pop(tweet['user']['screen_name'])
    
        if tweet['in_reply_to_status_id']:
        
            for member in tweet['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            if tweet['user']['screen_name'] in directed:
                directed.pop(tweet['user']['screen_name'])
    
        for member in tweet['entities']['user_mentions']:
            if member['screen_name'] not in directed:
                directed[member['screen_name']]=1
        
        if tweet['user']['screen_name'] in directed:
            directed.pop(tweet['user']['screen_name'])
    
        directed[tweet['user']['screen_name']]=1
    
    vector_template=[key for key,value in directed.items()]

    print(len(vector_template),' the size of vector templete')
    
    #collecting tire1 and tire2 users###########################################
    tire1=[user['user']['screen_name'] for user in db.users.find({'cluster_number':cluster_no})]
    tire2=[user['user']['screen_name'] for user in db.users.find({})]
    
    #printing days##############################################################
    print(days,' Days')
    
    #making the vector df#######################################################
    tweet_vectors=[]

    for tweet in tweets:
    
        directed={}
    
        for member in tweet['entities']['user_mentions']:
            if member['screen_name'] not in directed:
                directed[member['screen_name']]=1
        
        if tweet['user']['screen_name'] in directed:
            directed.pop(tweet['user']['screen_name'])
    
        if 'quoted_status' in tweet:
        
            for member in tweet['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            for member in tweet['quoted_status']['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            if tweet['quoted_status']['user']['screen_name'] not in directed:
                directed[tweet['quoted_status']['user']['screen_name']]=1
        
            if tweet['user']['screen_name'] in directed:
                directed.pop(tweet['user']['screen_name'])
    
        if tweet['in_reply_to_status_id']:
        
            for member in tweet['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            if tweet['user']['screen_name'] in directed:
                directed.pop(tweet['user']['screen_name'])
    
        for member in tweet['entities']['user_mentions']:
            if member['screen_name'] not in directed:
                directed[member['screen_name']]=1
        
        if tweet['user']['screen_name'] in directed:
            directed.pop(tweet['user']['screen_name'])
        ###############
        directed_keys=list(directed.keys())
        if(len(directed_keys)==0):
        
            tire=1
        else:
            count=0
            i=0
            while(count<1 and i<len(directed_keys)):
            
                if(directed_keys[i] in tire1):
                    count+=1
            
                i+=1
        
            if(count>0):
                tire=1
            else:
                count=0
                i=0
                while(count<1 and i<len(directed_keys)):
            
                    if(directed_keys[i] in tire2):
                        count+=1
            
                    i+=1
        
                if(count>0):
                    tire=2
                else:
                    tire=3
    
        tweet['tire']=tire
        #####################
        directed[tweet['user']['screen_name']]=1
    
        vector=[]
    
#     vector_template=[user['user']['screen_name'] for user in users]
    
        for member in vector_template:
        
            if member in directed:
                time=1+float(days.index(tweet['created_day'])/4)+float(0.25*tweet['tweeted_hour']/24)
                vector.append(time)
            else:
                vector.append(0)
    
#     day=tweet['created_day']/int(datetime.datetime(tweet['created_year'],12,31).strftime('%j'))
        day=float(days.index(tweet['created_day'])/4)
        hour=tweet['tweeted_hour']/24
    
        vector.append(day)
        vector.append(hour)
    
        tweet_vectors.append(vector)
    
    df=pd.DataFrame(tweet_vectors)
    
    #NOW CLUSTRING##############################################################
    print()
    print('Clustring')
    clustring=DBSCAN(eps=0.25,min_samples=1).fit(df)
    print('Clustring Finished')
    
    
    #making tweets df##############################################################
    tweet_df=pd.DataFrame(tweets)

    columns_to_remove=['_id','id_str','truncated', 'entities',
                       'source', 'in_reply_to_status_id', 'in_reply_to_status_id_str',
                       'in_reply_to_user_id', 'in_reply_to_user_id_str',
                       'in_reply_to_screen_name', 'geo', 'coordinates', 'place',
                       'contributors', 'is_quote_status',
                       'favorited', 'retweeted', 'lang',
                       'downloaded_day_year', 'downloaded_year',
                       'extended_entities', 'possibly_sensitive', 'quoted_status_id',
                       'quoted_status_id_str', 'quoted_status', 'retweeted_status']

    for column in columns_to_remove:
        try:
            tweet_df.drop(column,axis=1,inplace=True)
        except Exception as e:
            print(column,e.args)

    tweet_df['screen_name']=tweet_df['user'].apply(lambda x:x['screen_name'])
    tweet_df['friends_count']=tweet_df['user'].apply(lambda x:x['friends_count'])
    tweet_df['followers_count']=tweet_df['user'].apply(lambda x:x['followers_count'])
    tweet_df.drop('user',axis=1,inplace=True)

    tweet_df['tweeted_at']=tweet_df.apply(lambda row:datetime.datetime(row.created_year,1,1,row.tweeted_hour)+datetime.timedelta(row.created_day-1),axis=1)

    tweet_df['tweet_url']=tweet_df.apply(lambda row:f'https://twitter.com/{row.screen_name}/status/{row.id}',axis=1)
    tweet_df['cluster_no']=clustring.labels_
    
    #now doing tire level analytics################################################
    tire=int(input('plese enter tire number 1,2 or 3, to change cluster press 0 : '))
    
    #trends file path
    trends_path='E:/twitter_data/discover_weekly_data&report/trends.txt'
    
    while(tire!=0):
        
        #making thread_df based on the tire#######################################
        temp_df=tweet_df[tweet_df['tire']==tire]

        thread_df={}

        thread_df['cluster_no']=list(temp_df.groupby('cluster_no').count().reset_index()['cluster_no'])

        time_stamps=[]
        count=[]
        for i in thread_df['cluster_no']:
    
            time_df=temp_df[temp_df['cluster_no']==i]
            time_stamps.append(min(time_df['tweeted_at']))
            count.append(len(time_df))

        thread_df['time_stamps']=time_stamps
        thread_df['count']=count

        thread_df=pd.DataFrame(thread_df)
        
        #making plot_df#############################################################
        plot_df=pd.DataFrame(thread_df.groupby('time_stamps').count().reset_index()['time_stamps'])
        plot_df['thread_count']=thread_df.groupby('time_stamps').count().reset_index()['count']
        plot_df['tweet_count']=thread_df.groupby('time_stamps').sum().reset_index()['count']
        
        #printing the threshold threadcount##########################################
        print(2*plot_df['thread_count'].std()+plot_df['thread_count'].mean(),' is the threshold thread count')
        
        #getting time stamps above threshold#####################################
        stamps=list(plot_df[plot_df['thread_count']>(plot_df['thread_count'].mean()+2*plot_df['thread_count'].std())]['time_stamps'])
        
        #Arranging tweets#########################################################
        temp_df=tweet_df[tweet_df['tire']==tire]
        trend_df=temp_df[temp_df['tweeted_at'].apply(lambda time: True if time in stamps else False)]
        
        #now writing to the file
        with open(trends_path,'w',encoding='utf-8') as f:
            
            n_clusters_ = list(set(trend_df['cluster_no']))

            for i in n_clusters_:
    
                temp_df=trend_df[trend_df['cluster_no']==i]
                f.write(f"{i} : {len(temp_df)}\n")
                f.write('\n')
                for i in range(len(temp_df)):
                    f.write(str(temp_df.iloc[i]))
                    f.write('\n')
                    f.write('\n')
    
                f.write('----------------------------------------------------------------------------------------------\n')
        
        
        
        
        #getting tire again
        tire=int(input('plese enter tire number 1,2 or 3, to change cluster press 0 : '))
        
        
    
    
    
    
    
    
    #getting desicion again
    desicion=input('If you want to see trends press 1 else 0 : ')

print('thank you')
