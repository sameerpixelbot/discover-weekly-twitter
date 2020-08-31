# this file is for calculating bond between usersbased on last 7 days tweets
import pymongo
import datetime

#connecting to dB
client=pymongo.MongoClient()
db=client.twitter

#getting user data
users=[]
for user in db.users.find({}):
    users.append(user)

#today and seven days back
today=datetime.date.today()
seven_days_back=today - datetime.timedelta(days=7)

#doing for each user
i=0
for user in users:
    
    #nullifing the bonds
    for edge in user['edges']:
        edge['bond']=0
    
    #gettting past 7 days tweets
    tweets=[]
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
    
    #now calculating bond strength of all users connected for each tweet
    for tweet in tweets:
        
        #this is dict to store users who were directed
        directed={}
        
        tweet_weight=0.01
        weight=0.1
        
        #when retweeted
        if 'retweeted_status' in tweet:
            
            weight=1
        
            for member in tweet['entities']['user_mentions']:
                if member['screen_name'] not in directed:
                    directed[member['screen_name']]=1
        
            if tweet['user']['screen_name'] in directed:
                directed.pop(tweet['user']['screen_name'])
        
        #when quoted
        if 'quoted_status' in tweet:
            
            weight=10
            
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
        
        #when replied
        if tweet['in_reply_to_status_id']:
            
            weight=100
            
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
        
        #edge calculation for the tweet
        for edge in user['edges']:
            if edge['is_follower']:
                edge['bond']=edge['bond']+tweet_weight
            if edge['screen_name'] in directed:
                edge['bond']=edge['bond']+weight
    
    #printing user
    print(i,user['user']['screen_name'],' ',len(tweets))
    i+=1
    
    #updating to dB
    db.users.update_one({'_id':user['_id']},
                        {'$set':{'edges':user['edges']}})