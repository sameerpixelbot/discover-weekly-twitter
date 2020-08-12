#this file is used to scrape data using tweepy
import tweepy
import datetime
import pymongo

#connecting to mongodb
client=pymongo.MongoClient()
db=client.twitter

#getting to twitter api info
auth_path='E:/twitter_data/discover_weekly_data&report/auth.txt'

with open(auth_path,'r') as f:
    auth=f.read()

auth=auth.split(';')

for i in range(len(auth)):
    auth[i]=auth[i].split(',')

auth_no=int(input('Enter Auth number : '))

auth_details=tweepy.OAuthHandler(auth[auth_no][0],auth[auth_no][1])
auth_details.set_access_token(auth[auth_no][2],auth[auth_no][3])

api=tweepy.API(auth_details,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

#today
today=datetime.date.today()

#Prompting to get new user data or all user data
user_choice=int(input('For all users press 1, new users press 0 : '))

if user_choice==1:
    #getting all users from db
    users=[]
    for user in db.users.find({}):
        users.append(user['user']['screen_name'])

    #getting the number of days
    days=int(input('Enter the no of days : '))

    todaydt=datetime.datetime(today.year,today.month,today.day,0,0,0)
    startDate=todaydt-datetime.timedelta(days=days)
    endDate=startDate+datetime.timedelta(days=1)
else:
    #getting new users from db
    users=[]
    for user in db.users.find({'$and':[{'day_added':int(today.strftime('%j'))},{'year_added':int(today.year)}]}):
        users.append(user['user']['screen_name'])
    
    #getting the last 7 days tweets
    todaydt=datetime.datetime(today.year,today.month,today.day,0,0,0)
    startDate=todaydt-datetime.timedelta(days=7)
    endDate=todaydt-datetime.timedelta(days=2)

#empty list to collect statuses
tweets=[]
i=0
j=1

for user in users:
    
    i=i+1
    try:
        tmpTweets = api.user_timeline(user)
    except tweepy.TweepError:
        print('------ PRIVATE -----',i,user,j)
    
    print(i,user,j)
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweet._json['created_day']=int(tweet.created_at.strftime('%j'))
            tweet._json['created_year']=tweet.created_at.year
            tweets.append(tweet)
    
    try:
        while (tmpTweets[-1].created_at > startDate):
            print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
        
            i=i+1
        
            try:
                tmpTweets = api.user_timeline(user, max_id = tmpTweets[-1].id)
            except tweepy.TweepError:
                print('-----------',i,user,j)
            
            print(i,user,j)
            for tweet in tmpTweets:
                if tweet.created_at < endDate and tweet.created_at > startDate:
                    tweet._json['created_day']=int(tweet.created_at.strftime('%j'))
                    tweet._json['created_year']=tweet.created_at.year
                    tweets.append(tweet)
    except IndexError :
        print('*=*=*=*=  NO TWEETS BY  *=*=*=*=*=',user,j)
    j=j+1


#pulling json part of tweets status collected
tweets_json=[]
for status in tweets:
    tweets_json.append(status._json)

#inserting to database
i=0
for tweet in tweets_json:
    
    tweet['downloaded_day_year']=int(today.strftime('%j'))
    tweet['downloaded_year']=int(today.year)
    if '_id' in tweet:
        tweet.pop('_id')
        print(i)
    
    db.tweets.insert_one(tweet)
    i=i+1

#making a report card in a file

report_path='E:/twitter_data/discover_weekly_data&report/scraping_report.txt'

with open(report_path,'w') as f:
    no_tweets=f'Dumped in DataBase No of Tweets are : {len(tweets_json)} '
    day_report=f'{todaydt}, {startDate}, {endDate}'
    f.writelines([no_tweets,day_report])
    
    
    
print('Dumped in DataBase No of Tweets are : ',len(tweets_json))
print(todaydt,' ',startDate,' ',endDate)