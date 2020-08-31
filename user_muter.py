#this file is to list muted users for seven days

#path to users discovered
user_path='E:/twitter_data/discover_weekly_data&report/users.txt'
#getting users list
with open(user_path,'r') as f:
    users=f.read()

#list of users who got through manual inspection
users={user.split(':')[0][:-1].split("'")[-1]:int(user.split(':')[1]) for user in users[1:-1].split(',')}
users=[user[1:] for user in list(users.keys()) if user[0]=='-']

muted_users={}

#muting for next seven days
for user in users:
    muted_users[user]=7

#decreasing the mute limit on existing users in mute_list file
mute_path='E:/twitter_data/discover_weekly_data&report/mute_list.txt'
#getting muted users
with open(mute_path,'r') as f:
    users=f.read()

#converting read str to dict
users={user.split(':')[0][:-1].split("'")[-1]:int(user.split(':')[1]) for user in users[1:-1].split(',')}
#decreasing values
user_list=list(users.keys())
for user in user_list:
    users[user]-=1
    if users[user]==0:
        users.pop(user)

muted_users.update(users)

muted_users=dict(sorted(muted_users.items(),key=lambda x:x[1],reverse=True))
#writing to file
with open(mute_path,'w') as f:
    f.write(str(muted_users))

####################################################################################    
#dealing with blocked user
    
#getting users list
with open(user_path,'r') as f:
    users=f.read()


#list of users who got through manual inspection
users={user.split(':')[0][:-1].split("'")[-1]:int(user.split(':')[1]) for user in users[1:-1].split(',')}
users=[user[1:] for user in list(users.keys()) if user[0]=='/']

blocked_users={}

#muting for next seven days
for user in users:
    blocked_users[user]=7

#block path
block_path='E:/twitter_data/discover_weekly_data&report/block_list.txt'
#getting muted users
with open(block_path,'r') as f:
    users=f.read()

#converting read str to dict
users={user.split(':')[0][:-1].split("'")[-1]:int(user.split(':')[1]) for user in users[1:-1].split(',')}

blocked_users.update(users)
#writing to file
with open(block_path,'w') as f:
    f.write(str(blocked_users))