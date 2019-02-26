# account_id = '@yuu116atlab'
# app_name = PeriodicRetweetor
# url = 'https://developer.twitter.com/en/apps/14806562'
import os
ck_ = os.getenv('TW_API_CONSUMER_KEY',None)
cs_ = os.getenv('TW_API_CONSUMER_SECRET',None)
at_ = os.getenv('TW_API_ACCESS_TOKEN',None)
as_ = os.getenv('TW_API_ACCESS_TOKEN_SECRET',None)
if len([ _ for _ in [ck_, cs_, at_, as_] if _ == None ]) >= 1 :
    raise ValueError("must set tw api token.")
    
consumer = { 'key' : ck_, 'secret' : cs_, }
access = { 'token' : at_, 'token_secret' : as_, }
