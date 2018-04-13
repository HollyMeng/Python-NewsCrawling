# -*- coding: utf-8 -*

import requests
from bs4 import BeautifulSoup
import re
import bs4
from datetime import datetime
import json
import pandas as pd

def getHTMLText(url):
    try:
        r=requests.get(url,timeout=30)  #爬取不受限制的网页
        # kv = {'user-agent': 'Mozilla/5.0'}
        # r=requests.get(url,headers=kv)  #爬取受限制的网页，要先把headers伪装成浏览器
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def getNewsInfo(news_url,comment_url):
    result={}
    html = getHTMLText(news_url)
    soup = BeautifulSoup(html,"html.parser") #
    result['title']=soup.select('.main-title')[0].text  #获取新闻标题，时间，内容，编辑人
    date_string=soup.select('.date')[0].text
    result['date']=datetime.strptime(date_string,'%Y年%m月%d日 %H:%M')
    result['source']=soup.select('.source')[0].text
    # print(title,dt,source)

    article=[]
    for p in soup.select('#article p')[:-1]:  #[:-1]去掉最后一个元素
        article.append(p.text.strip())
    result['article']=article
    # print(article)
    # '@'.join(article)  # 段落之间用空白隔开

    editor=soup.select('.show_author')[0].text.strip('责任编辑：')
    # print(editor)
    result['editor']=editor

    m = re.search('doc-i(.*).shtml', news_url)
    newsid = m.group(1)  # group(1)括号里写0就是全部比对的部分，1就是只有小括号内的部分
    comment = getHTMLText(comment_url.format(newsid))  #
    jd = json.loads(comment.strip('var data='))   #获取json格式的评论数
    comment = jd['result']['count']['total']
    result['comments']=comment
    # print(result)
    return result


# def getNewsId(news_url):
#     # 获取新闻id
#     # 方法1-观察id位置，然后去除左右多余字符
#     # newsid = url.split('/')[-1].rstrip('.shtml').lstrip('doc-i')
#     # print(newsid)
#
#     # 方法2-正则表达式
#     m = re.search('doc-i(.*).shtml', news_url)
#     newsid = m.group(1)  # group(1)括号里写0就是全部比对的部分，1就是只有小括号内的部分
#     return newsid

# def getCommentCount(news_url,comment_url):
#
#     newsid=getNewsId(news_url)
#     comment=getHTMLText(comment_url.format(newsid)) #
#     jd = json.loads(comment.strip('var data='))
#     comment = jd['result']['count']['total']
#     # print(comment)
#     return comment

def parseListLinks(url,comment_url):
    newsdetails=[]
    html_mulpage = getHTMLText(url)
    jd = json.loads(html_mulpage.lstrip(' newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        newsdetails.append(getNewsInfo(ent['url'],comment_url))
    return newsdetails

if __name__=="__main__":
    news_url = "http://news.sina.com.cn/c/nd/2018-03-28/doc-ifysqfnh9642370.shtml"
    comment_url = "http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gn&newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3"

    # getNewsInfo(news_url,comment_url)

    #分页信息
    url_mulpage="http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}"
    news_total=[]
    for i in range(1,4):
        print(i)
        news_total.extend(parseListLinks(url_mulpage.format(i),comment_url))
    # print(news_total)

    df=pd.DataFrame(news_total)
    print(df.head(10))

    df.to_csv('news.csv',encoding="utf_8_sig")

    # 保存到数据库的代码无法运行
    # import sqlite3
    # with sqlite3.connect('news.sqlite3') as db:
    #     df.to_sql('news',con=db)











