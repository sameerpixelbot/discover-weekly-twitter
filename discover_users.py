#this file is to make a list of users not in our present users how are very active
#libraries needed
import pymongo
import datetime

#connecting to dB
client=pymongo.MongoClient()
db=client.twitter

#todays day year
day=int(datetime.date.today().strftime('%j'))
today=datetime.date.today()

#empty tweets list for last 7 days
tweets=[]

#getting tweets

if day-7>=0:
    tweets=[tweet for tweet in db.tweets.find({'$and':[{'downloaded_day_year':{'$gt':day-7}},{'downloaded_year':today.year}]})]
else:
    tweets=[tweet for tweet in db.tweets.find({'$and':[{'downloaded_day_year':{'$gt':0}},{'downloaded_year':today.year}]})]
    
    last_year_days=int(datetime.datetime(today.year-1,12,31).strftime('%j'))
    last_tweets=[tweet for tweet in db.tweets.find({'$and':[{'downloaded_day_year':{'$gt':last_year_days+day-7}},{'downloaded_year':today.year-1}]})]
    for tweet in last_tweets:
        tweets.append(tweet)

#counting mentions
replied_to={}

for tweet in tweets:
    user_mentions=tweet['entities']['user_mentions']
    for user in user_mentions:
        if user['screen_name'] not in replied_to:
            replied_to[user['screen_name']]=1
        else:
            replied_to[user['screen_name']]=replied_to[user['screen_name']]+1

#getting the already present in our dB
users=[]
for user in db.users.find({}):
    users.append(user['user']['screen_name'])

#removing the already present ones
for user in users:
    if user in replied_to:
        replied_to.pop(user)

#sorting all based on no of replies
replied_to=sorted(replied_to.items(),key=lambda x:x[1],reverse=True)

#getting the percentage
percentage=float(input(f'The number of people is {len(replied_to)}, Please enter percentage : '))/100
replied_to=replied_to[:int(len(replied_to)*percentage)]

#printing in users.txt
user_path='E:/twitter_data/discover_weekly_data&report/users.txt'

with open(user_path,'w') as f:
    f.write(str(replied_to))