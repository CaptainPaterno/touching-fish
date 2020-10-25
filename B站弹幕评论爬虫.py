#!/usr/bin/env python
# coding: utf-8

# In[4]:


import requests
import json
import time
import random
from bs4 import BeautifulSoup as BS


# # Headers

# In[5]:


useful_user_agent = [
'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',

'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',

'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0',

'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)',

'Mozilla/4.0(compatible;MSIE6.0;WindowsNT5.1)',

'Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',

'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',

'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11',

'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',

'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)',

'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)']

def download_comment_header():
    return {
    'authority': 'api.bilibili.com',
    'method': 'GET',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'referer': 'https://www.bilibili.com/',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': random.choice(useful_user_agent)
}


# # 获得所有视频

# In[8]:


#upid: up主的个人id， ps: page size, pn: page number
def all_video_url(upid, ps, pn):
    return "https://api.bilibili.com/x/space/arc/search?mid=" + str(upid) + "&ps=" + str(ps) + "&tid=0&pn=" + str(pn) + "&keyword=&order=pubdate&jsonp=jsonp"


# In[9]:


#upid: up主的个人id， ps: page size
#return: 以视频avid为key的dict，包含bvid和title
def get_info_all_video(upid, ps):
#     ps = 50
#     upid = 546195
    r = requests.get(all_video_url(upid,ps,1), headers = all_video_header)

    jsonText = json.loads(r.text)
    totalVideoNums = jsonText['data']['page']['count']
    page = (totalVideoNums - 1)//ps + 1
    videoInfo = {}
    vlist = jsonText['data']['list']['vlist']
    print("-------------Doing page{}---------------".format(1))
    for v in vlist:
        videoInfo[v['aid']] = [v['bvid'], v['title']]
    for i in range(2, page + 1):
        r = requests.get(all_video_url(upid,ps,i), headers = all_video_header)
        jsonText = json.loads(r.text)
        vlist = jsonText['data']['list']['vlist']
        print("-------------Doing page{}---------------".format(i))
        for v in vlist:
            videoInfo[v['aid']] = [v['bvid'], v['title']]
    print('Done!')
    return videoInfo


# In[10]:


#pn: page number, oid: 视频id(av)
def get_comment_url(pn, oid):
    return 'https://api.bilibili.com/x/v2/reply?&jsonp=jsonp&pn={}&ps=50&type=1&oid={}&sort=2&_=1603036280474'.format(pn, oid)


# In[11]:


#oid: 视频id(av)
#return: [(用户名，评论)，(用户名，评论)...]
def get_comment(oid):
    t = time.time()
    pn = 1
#     oid = 457025973
    try:
        r = requests.get(get_comment_url(pn,oid), headers = download_comment_header())
        jsonText = json.loads(r.text)
        count = jsonText['data']['page']['count']
        comments = []
        pages = count // 20 + (0 if count % 20 == 0 else 1)
        for i in jsonText['data']['replies']:
            comments.append(i['content']['message'])
        while(pn < pages):
            #不sleep会被封，封了需要换user-agent
            time.sleep(1)
            pn += 1
            r = requests.get(get_comment_url(pn,oid), headers = download_comment_header)
            jsonText = json.loads(r.text)
            for i in jsonText['data']['replies']:
                comments.append((i['member']['uname'], i['content']['message']))
        len(comments)
        print(len(comments))
    except:
        print("GG")  
    print(time.time() - t)
    return comments


# In[16]:


#TODO: json['data']返回的是所有分视频的cid信息，需要额外操作
#oid: 视频id(av)
def get_cid(oid):
    url = 'http://api.bilibili.com/x/player/pagelist?callback=jsonp&aid={}'.format(oid)
    r = requests.get(url = url, headers = download_comment_header())
    return json.loads(r.text)['data'][0]['cid']


# In[13]:


#cid: 细分视频id
def get_danmu_url(cid):
    url = 'https://comment.bilibili.com/{}.xml'.format(cid)
    return url


# In[32]:


#oid: 视频id(av)
#return: [time, timestamp, userid, danmuid, 弹幕]
def get_danmu(oid):
#     oid = 457025973
    url = get_danmu_url(get_cid(oid))
    r = requests.get(url = url, headers = download_comment_header())
    formated_file = BS(r.content, "lxml")
    danmu = []
    for dm in formated_file.find_all('d'):
        text = dm.get_text()
        info = dm["p"].split(",")
        if text == '':
            continue
        danmu.append([info[0], info[4], info[6], info[7], text])
    
    return danmu


# In[51]:


# f = open("comments.txt", "w")
# t = time.time()
# oid = 457025973
# comment = get_comment(oid)
# print(time.time()-t)
# print(len(comment))


# In[52]:


# import codecs
# def output(danmu, comment):
#     f = codecs.open("danmus.txt", "w", "utf-8")
#     for i in danmu:
#         f.write(i.encode('utf-8').decode('utf-8'))
#         f.write("\n")
#     f.close()
#     f = codecs.open("comments.txt", "w", "utf-8")
#     for i in comment:
#         f.write(i[0])
#         f.write(": ")
#         f.write(i[1])
#         f.write("\n")
#     f.close()


# In[53]:


# oid = 457025973
# url = get_danmu_url(get_cid(oid))
# r = requests.get(url = url, headers = download_comment_header())


# In[54]:


# formated_file = BS(r.content, "lxml")
# danmu = []
# for dm in formated_file.find_all('d'):
#     text = dm.get_text()
#     info = dm["p"].split(",")
#     if text == '':
#         continue
#     danmu.append([info[0], info[4], info[6], info[7], text])


# In[55]:


# type(dm)
# dm["p"].split(",")


# In[57]:


# import codecs
# f = codecs.open("danmus.txt", "r", "utf-8")


# In[58]:


# danmu = f.read().split()
# danmu[3]


# In[59]:


# import jieba
# from queue import PriorityQueue as PQ
# ' '.join(jieba.cut(danmu[3], cut_all = True))


# In[60]:


# dic = {}
# for i in danmu:
#     fenci = ' '.join(jieba.cut(i)).split()
#     for j in fenci:
#         if j in dic:
#             dic[j] += 1
#         else:
#             dic[j] = 1
# pq = PQ()
# index = 0
# for i in dic:
#     index += 1
#     pq.put([10000 - dic[i], index, i])
# while not pq.empty():
#     a = pq.get()
#     print(10000 - a[0], a[2])


# In[ ]:




