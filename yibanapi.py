#coding=utf8

import requests
import json
import time
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yiban.settings")
django.setup()
from main.models import User

session = requests.session()
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi Note 5 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36 yiban_android",
    "Host": "www.yiban.cn",
    "loginToken" : ""}


def loginYiban(username, password):
    url = "https://mobile.yiban.cn/api/v2/passport/login?account=%s&passwd=%s&ct=2&app=1&v=4.5.9&apn=wifi&identify=868773033477236&sig=000fcc637ac7efd1&token=&device=XiaomiRedmi+Note+5&sversion=27" % (username, password)
    response = session.get(url,verify=True).text
    json_response = json.loads(response)
    if json_response['response'] == 415:
        return False, False, False, False
    if json_response['response'] == 100:
        userid = json_response['data']['user']['schoolOrganization']['user_id']
        name = json_response['data']['user']['name']
        logintoken_accrss = json_response['data']['access_token']
        logintoken = json_response['data']['token']
        headers['loginToken'] = logintoken
        return userid, logintoken, logintoken_accrss, name
    else:
        return False, False, False, False
def getNews(userid):
    url = "https://www.yiban.cn/forum/article/listAjax"
    data = {"channel_id":"215878",
            "group_id":"383290",
            "puid":userid,
            "page":"1",
            "size":"5",
            "orderby":"updateTime",
            "Sections_id":"-1",
            "need_notice":"0",
            "my":"0",
            "lastId":"0"}
    resp = session.post(url=url,data=data, verify=True).text
    json_data = json.loads(resp)['data']['list']
    return json_data

def postMessage(userid,logintioken, blogtext):
    json_data=getNews(userid)
    for ln in json_data:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi Note 5 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36 yiban_android",
            "Host": "www.yiban.cn",
            "Origin": "http://www.yiban.cn",
            "Referer": "http://www.yiban.cn/forum/article/show/channel_id/215878/puid/%s/article_id/%s/group_id/383290" % (userid, ln['id']),
            "Cookie": "YB_SSID=d310b894672cf9a04516a10ce91d9968; yiban_user_token="+logintioken}
        url = "http://www.yiban.cn/forum/reply/addAjax"
        data={"channel_id":"215878",
              "puid":userid,
              "article_id":ln['id'],
              "content":blogtext,
              "reply_id":"",
              "images":"",
              "syncFeed":"1",
              "isAnonymous":"0"}
        resp = session.post(url,data=data, verify=True,headers=headers).text
        print(json.loads(resp)['message'])

def postMiaomiao(logintoken, pushtext):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi Note 5 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36 yiban_android",
        "Host": "ymm.yiban.cn",
        "Origin": "http://www.yiban.cn",
        "loginToken" :logintoken,
        "Cookie": "YB_SSID=d310b894672cf9a04516a10ce91d9968; yiban_user_token="+logintoken}
    url = "http://ymm.yiban.cn/article/index/add?loginToken="+logintoken+"&content="+pushtext
    data={"content":pushtext}
    resp = session.post(url,data=data, verify=True,headers=headers).text
    print(json.loads(resp)['message'])

def logout(logintoken):
    url = "https://mobile.yiban.cn/api/v1/passport/logout?access_token=%s&access_token=%s" % (logintoken, logintoken)
    response = session.get(url,verify=True).text
    json_response = json.loads(response)
    if json_response['response'] == 100:
        return True
    else:
        return False    

def every(logintoken):
    url = "https://mobile.yiban.cn/api/v3/checkin/question?access_token="+logintoken
    resp = session.get(url, verify=True,headers=headers).text
    print(resp)
    answer = json.loads(resp)['data']['survey']['question']['option'][0]['id']
    url = "https://mobile.yiban.cn/api/v3/checkin/answer?access_token=%s&optionId=%s" % (logintoken, answer)
    session.post(url, verify=True, headers=headers)

def dowhile(username, password, blogtext, pushtext):
    userid, logintoken,logintoken_accrss,name = loginYiban(username, password)
    if userid != False:
        postMessage(userid,logintoken, blogtext) #回帖
        postMiaomiao(logintoken, pushtext) #易喵喵
        every(logintoken_accrss) #签到
        logout(logintoken)

if __name__ == '__main__':
    while True:
        nowHour = time.strftime('%H',time.localtime(time.time()))
        if nowHour=='08':
            users = User.objects.all()
            for user in users:
                dowhile(user.username, user.password, user.blogtext, user.pushtext)
        time.sleep(3600)