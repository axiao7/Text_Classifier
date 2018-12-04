#coding=utf-8


# Script Name:      news_spider.py
# Author:           lszero
# Created:          November 12, 2015
# Last Modified:    December 29, 2015
# Version:          1.0
# Description:      The current version only support 'www.chinanews.com'(中国新闻网).

import sys,time,datetime
import MySQLdb
import requests
from bs4 import BeautifulSoup
import importlib
# import threading
importlib.reload(sys)
# sys.setdefaultencoding('utf-8')

site_source_list = ["chinanews"]
class NewsSpider:
    def connectDB(self, db_host, db_user, db_passwd, db_name, db_port):
        try:
            self.conn = MySQLdb.connect(host=db_host,user=db_user,passwd=db_passwd,db=db_name,port=db_port, use_unicode=True, charset="utf8")
            self.cur = self.conn.cursor()
            print ("Connect database successfully.")
        except e:
            print ("MySQL Error %d: %s" % (e.args[0], e.args[1]))

    def closeDB():
        self.cur.close()
        self.conn.close()
        print ("Close database.")

    def getNewsToDB(self, table, str_start_time, str_end_time):
        count = 0
        date_range = self.dateRange(str_start_time, str_end_time)
        
        for date in date_range:
            self.strYear = str(date.year)
            if date.month < 10:
                self.strMonth = "0" + str(date.month)
            else:
                self.strMonth = str(date.month)

            if date.day < 10:
                self.strDay = "0" + str(date.day)
            else:
                self.strDay = str(date.day)

            for source in site_source_list:
                roll_page_url = self.getRollPageUrl(table, source, self.strYear, self.strMonth, self.strDay)
                # numflag = [0, 0, 0, 0, 0, 0, 0]
                # for x in range(5):
                # threading.Thread(target=self.getNewsInfoFromRollPage(source, roll_page_url,1,5)).start()
                # threading.Thread(target=self.getNewsInfoFromRollPage(source, roll_page_url,2,5)).start()
                # threading.Thread(target=self.getNewsInfoFromRollPage(source, roll_page_url,3,5)).start()
                # threading.Thread(target=self.getNewsInfoFromRollPage(source, roll_page_url,4,5)).start()
                # threading.Thread(target=self.getNewsInfoFromRollPage(source, roll_page_url,5,5)).start()

                n=self.getNewsInfoFromRollPage(table, source, roll_page_url)
                # n = self.getNewsInfoFromRollPage(source, roll_page_url)
                count += n
                # count=111111
        print (str(count) + " data added.")

    def getNewsInfoFromRollPage(self, table, site_source, roll_page_url):
        count = 0
        # tutol=tutol
        # i = 0
        # offset=offset
        response = requests.get(roll_page_url,timeout=(3, 5))
        response.encoding = "gb18030"
        soup = BeautifulSoup(response.text, "html.parser")

        if site_source == "chinanews":
            newsInfoList = soup.find_all("div", class_="dd_lm")

            for info in newsInfoList:
                # i = i + 1
                # if i<=numflag[offset]:
                #     print("break",numflag[offset])
                #     continue
                #
                # numflag[offset]=i
                # if i%tutol!=offset:
                #     print("break",i,tutol,offset)
                #     continue
                # print("跳出循环",i,tutol,offset)
                theme = info.text[1:-1]
                info = info.next_sibling.next_sibling
                title = info.text
                url = info.a["href"]
                if url[:4] != "http":   #前面自带http的是视频新闻，跳过
                    url = "http://www.chinanews.com" + url



                b_checked = False
                sql_query = "select * from " + table + " where url='" + url + "'"
                # print(sql_query)
                self.cur.execute(sql_query)
                for item in self.cur.fetchall():
                    b_checked = True
                    break

                if b_checked == True:
                    continue


                try:
                    news = self.getNewsFromURL(url, site_source)
                    content = news[1]
                except:
                    content=""
                    print("发生错误")

                # print title
                # print theme
                # print content

                if content == "":
                    continue

                time = info.next_sibling.text
                tmp_time = time.split(' ')
                datetime = self.strYear + "-" + self.strMonth + "-" + self.strDay + " " + tmp_time[1] + ":00"

                try:
                    sql_insert = "insert into " + table + "(title,content,theme,date,url) values(%s,%s,%s,%s,%s)"
                    # print(sql_insert)
                    self.cur.execute(sql_insert, (title, content, theme, datetime,url))

                    self.conn.commit()
                    count += 1
                except  e:
                    print ("MySQL Error %d: %s" % (e.args[0], e.args[1]))
                print(url)
        return count
        
    def getNewsFromURL(self, url, site_source='chinanews'):
        try:
            response = requests.get(url,timeout=(3,5))
        except:
            print("1111111这个出错")
        response.encoding = "gb18030"
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            title = soup.find("title").string
        except:
            title=""
        content = ""

        if site_source == "chinanews":
            post = soup.find("div", class_="left_zw")
            if post == None:
                return ""

            pList = post.find_all("p")
            for p in pList:
                for sub_node in p.children:
                    if sub_node.string != None:
                        content += sub_node.string
                        
        return title, content


    def getRollPageUrl(self, table, site_source, strYear, strMonth, strDay):
        if site_source == "chinanews":
            return "http://www.chinanews.com/scroll-news/" + table + "/" + strYear + "/" + strMonth + strDay + "/news.shtml"

    def dateRange(self, str_start_time, str_end_time):
        t1 = str_start_time.split('-')
        t2 = str_end_time.split('-')
        start_time = datetime.datetime(int(t1[0]), int(t1[1]), int(t1[2]))
        end_time = datetime.datetime(int(t2[0]), int(t2[1]), int(t2[2]))
        for i in range(int((end_time-start_time).days) + 1):
            yield start_time + datetime.timedelta(i)


def main():
    '''
    spider = NewsSpider()
    news = spider.getNewsFromURL('http://www.chinanews.com/cj/2015/12-29/7693062.shtml')
    print news[0]   # title
    print news[1]   # content
    '''
    table = 'ty'
    t1 = time.time()
    spider = NewsSpider()
    spider.connectDB(db_host='localhost', db_user='lwx', db_passwd='lwx32111', db_name='data_mining', db_port=3306)
    spider.getNewsToDB(table, "2017-1-4", "2017-6-26")
    spider.closeDB()
    t2 = time.time()
    print ("Execution time: %.3f s." % (t2 - t1))

if __name__ == '__main__':
    main()
