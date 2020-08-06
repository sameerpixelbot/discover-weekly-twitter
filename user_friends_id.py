#this script is to get the friends list of all the users

import pymongo
import tweepy
import datetime
import time

#getting to twitter api info
auth_path='E:/twitter_data/discover_weekly_data&report/auth.txt'

with open(auth_path,'r') as f:
    auth=f.read()

auth=auth.split(';')

for i in range(len(auth)):
    auth[i]=auth[i].split(',')

#getting users from mongodb
client=pymongo.MongoClient()
db=client.twitter

#today
today=datetime.date.today()

#Prompting to get new user data or all user data
user_choice=int(input('For all users press 1, new users press 0 : '))

#for all users
if user_choice==1:
    users=[]
    for user in db.users.find({}):
        users.append(user)
else:
    users=[]
    for user in db.users.find({'$and':[{'day_added':int(today.strftime('%j'))},{'year_added':int(today.year)}]}):
        users.append(user)

#friends_report.txt file path to save the status as it may take long hours to do this
friends_report_path='E:/twitter_data/discover_weekly_data&report/friends_report.txt'

#checking if the previous attempt was un succesful
was_done=int(input('Was the previous attempt succesful if yes press 1 else no press 0 : '))

#taking the choice of to where to start
if was_done==1:
    user_no=0
else:
    with open(friends_report_path,'r') as f:
        user_no=int(f.read())-1

#collecting data  
auth_no=0

auth_details=tweepy.OAuthHandler(auth[auth_no%len(auth)][0],auth[auth_no%len(auth)][1])
auth_details.set_access_token(auth[auth_no%len(auth)][2],auth[auth_no%len(auth)][3])

api=tweepy.API(auth_details,wait_on_rate_limit_notify=True)


while user_no<len(users):
    try:
        i=0
        friends=[]
        for id in tweepy.Cursor(api.friends_ids, screen_name=users[user_no]['user']['screen_name']).items():
            friends.append({'id':id})
            i=i+1
        #Printing Status
        print(i,users[user_no]['user']['screen_name'],user_no)
        #updating dB
        db.users.update_one({'_id':users[user_no]['_id']}, {'$set':{'friends_id':friends}})
        
        #writing status to friends_report.txt file in case it stops mid way
        with open(friends_report_path,'w') as f:
            f.write(str(user_no))
        
        user_no=user_no+1
    except Exception as e:
        
        print(1,' ',e.args)
        try:
            if e.args[0][0]['message']=='Rate limit exceeded':
            
                auth_no=auth_no+1
            
                auth_details=tweepy.OAuthHandler(auth[auth_no%len(auth)][0],auth[auth_no%len(auth)][1])
                auth_details.set_access_token(auth[auth_no%len(auth)][2],auth[auth_no%len(auth)][3])
            
                api=tweepy.API(auth_details,wait_on_rate_limit_notify=True)
            
                try:
                    i=0
                    friends=[]
                    for id in tweepy.Cursor(api.friends_ids, screen_name=users[user_no]['user']['screen_name']).items():
                        friends.append({'id':id})
                        i=i+1
                    #Printing Status
                    print(i,users[user_no]['user']['screen_name'],user_no)
                    #updating dB
                    db.users.update_one({'_id':users[user_no]['_id']}, {'$set':{'friends_id':friends}})
        
                    #writing status to friends_report.txt file in case it stops mid way
                    with open(friends_report_path,'w') as f:
                        f.write(str(user_no))
        
                    user_no=user_no+1
                except Exception as e:
                
                    print(2,' ',e.args)
                    try:
                        if e.args[0][0]['message']=='Rate limit exceeded':
                            print('Sleeping..',auth_no%len(auth))
                            time.sleep(60)
                    except Exception as e:
                        print(3,' ',e.args)
                        print('skipping user : ',users[user_no]['user']['screen_name'],user_no)
                        user_no=user_no+1
            
            
        except Exception as e:
            print(4,' ',e.args)
            print('skipping user : ',users[user_no]['user']['screen_name'],user_no)
            user_no=user_no+1

            
            
