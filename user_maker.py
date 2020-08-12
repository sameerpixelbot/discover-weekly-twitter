#this file is used to upload user json objects in mongodb-twitter-users
import pymongo
import tweepy
import datetime

#users file path
user_path='E:/twitter_data/discover_weekly_data&report/users.txt'
#getting the users list
with open(user_path,'r') as f:
    users=f.read()

#list of users who got through manual inspection
users={user.split(':')[0][:-1].split("'")[-1]:int(user.split(':')[1]) for user in users[1:-1].split(',')}
users=[user[1:] for user in list(users.keys()) if user[0]=='*']

#connect with twitter api 
auth_path='E:/twitter_data/twitter_home_data/auth.txt'

with open(auth_path,'r') as f:
    auth=f.read()
#auth details
auth=auth.split(',')

auth_details=tweepy.OAuthHandler(auth[0],auth[1])
auth_details.set_access_token(auth[2],auth[3])

api=tweepy.API(auth_details,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

#today date
today=datetime.date.today()
#making user objects
user_objects=[]
i=0
for user in users:
    
    try :
        #getting user details
        user=api.get_user(id=user)
        #collecting data from _json feild
        user_json=user._json
        
        #building user object
        user_dict={}
        user_dict['user']={}
        user_dict['user']['screen_name']=user_json['screen_name']
        user_dict['user']['id']=user_json['id']
        user_dict['user']['id_str']=user_json['id_str']
        user_dict['user']['name']=user_json['name']
        user_dict['friends_id']=[]
        user_dict['edges']=[]
        
        core_user=bool(input(f"The user is {user_json['screen_name']}, press any for True, press nothing for False : "))
        user_dict['core_user']=core_user
        user_dict['activity']=0
        user_dict['day_added']=int(today.strftime('%j'))
        user_dict['year_added']=int(today.year)
        

        #inserting in user_objects list
        user_objects.append(user_dict)
    except tweepy.TweepError:
        print(i,' ',user)
    i=i+1

#connecting to mongodb
client=pymongo.MongoClient()
db=client.twitter

#inserting in users collection
for user in user_objects:
    db.users.insert_one(user)
