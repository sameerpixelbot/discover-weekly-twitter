#this file is to manually delete users
import pymongo

#getting the screen_name
screen_name=input('Please enter the name of user : ')

#connecting to db
client=pymongo.MongoClient()
db=client.twitter

#getting users
users=[]
for user in db.users.find({}):
    users.append(user)

print(len(users))

for user in users:
    
    if user['user']['screen_name']==screen_name:
        _id=user['_id']
    
    for i in range(len(user['edges'])):
        if user['edges'][i]['screen_name']==screen_name:
            pos=i
    
    try:
        user['edges'].pop(pos)
    except Exception as e:
        print(e)
    
    db.users.update_one(
        {'_id':user['_id']},
        {'$set':{'edges':user['edges']}})

#removing user
db.users.delete_one({'_id':_id})