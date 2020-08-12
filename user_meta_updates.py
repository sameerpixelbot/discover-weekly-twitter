#this file is to update the user meta data
import pymongo
import datetime

#connecting to dB
client=pymongo.MongoClient()
db=client.twitter

#getting user data
users=[]
for user in db.users.find({}):
    users.append(user)

#setting days
today=datetime.date.today()
seven_days_back=today - datetime.timedelta(days=7)

#calculating activity of each user

if seven_days_back.year==today.year :
    
    for user in users:
        
        activity=0
        for tweet in db.tweets.find({'$and':[{'user.id':user['user']['id']},
                                     {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]},
                                     {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}
                                     ]}):
            activity=activity + 1
            
        #updating in dB
        db.users.update_one({'_id':user['_id']},
                            {'$set':{'activity':activity}})

else:
    
    for user in users:
        
        activity=0
        for tweet in db.tweets.find({'$and':[{'user.id':user['user']['id']},
                                     {'$and':[{'created_day':{'$gt':int(seven_days_back.strftime('%j'))}},{'created_year':seven_days_back.year}]}
                                     ]}):
            activity=activity+1
        
        for tweet in db.tweets.find({'$and':[{'user.id':user['user']['id']},
                                     {'$and':[{'created_day':{'$lte':int(today.strftime('%j'))}},{'created_year':today.year}]}
                                     ]}):
            activity=activity+1
            
        #updating in dB
        db.users.update_one({'_id':user['_id']},
                            {'$set':{'activity':activity}})

#getting new users for edges update
new_users=users

for user in users:
    
    for new_user in new_users:
        
        if user['user']['id'] != new_user['user']['id']:
            #checking if he is already there in edges
            is_connected=False
            for edge in user['edges']:
                if new_user['user']['id'] ==edge['id']:
                    is_connected=True
            if not is_connected:
                edge={}
                edge['id']=new_user['user']['id']
                edge['screen_name']=new_user['user']['screen_name']
                #checking if he is a follower
                is_follower=False
                for id in new_user['friends_id']:
                    if id['id']==user['user']['id']:
                        is_follower=True
                
                edge['is_follower']=is_follower
                edge['bond']=0
                user['edges'].append(edge)
    
    db.users.update_one({'_id':user['_id']},{'$set':{'edges':user['edges']}})

