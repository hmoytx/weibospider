# -*- coding:utf-8 -*-

import urllib2
import urllib
from threading import Thread
from Queue import Queue
import re
import os
import sys
import time



PARSE_EXIT = False
COLLECT_EXIT = False
DOWNLOAD_EXIT = False


class pageCollect(Thread):
    def __init__(self, pageQueue, dataQueue):
        super(pageCollect, self).__init__()
        self.pageQueue = pageQueue
        self.dataQueue = dataQueue
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1"
        }

    def run(self):
        while not COLLECT_EXIT:
            try:
                url = self.pageQueue.get(False)
                request = urllib2.Request(url, headers=self.headers)
                response = urllib2.urlopen(request)
                self.dataQueue.put(response.read())
            except:
                pass


class contentParse(Thread):
    def __init__(self, dataQueue, linkQueue):
        super(contentParse, self).__init__()
        self.dataQueue = dataQueue
        self.linkQueue = linkQueue

    def run(self):
        while not PARSE_EXIT:
            try:
                content = self.dataQueue.get(False)
                pattern = re.compile(r'"url":"(.*?)"')
                links = pattern.findall(content)
                for url in links:
                    if len(url) == 71:
                        url1 = url.replace("\/", "/")
                        src = url1.replace("thumb180", "large")
                        #print src
                        self.linkQueue.put(src)
            except:
                pass



class downloadPic(Thread):
    def __init__(self, linkQueue, nameQueue, Dirpath):
        super(downloadPic, self).__init__()
        self.linkQueue = linkQueue
        self.nameQueue = nameQueue
        self.Dirpath = Dirpath
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1"
        }


    def run(self):
        while not DOWNLOAD_EXIT:
            try:
                src = self.linkQueue.get(False)
                #print src
                request = urllib2.Request(src, headers=self.headers)
                response = urllib2.urlopen(request)
                filename = str(self.nameQueue.get(False)) + '.jpg'
                with open(str(self.Dirpath)+"/"+filename, "w") as f:
                    f.write(response.read())
            except:
                pass


def mkDir(dirName):
    """
    创建保存目录
    """
    dirpath = os.path.join(sys.path[0], dirName)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    return dirpath



def main(url, pages, Dirpath):

    # 收集页面url
    pageQueue = Queue()
    # 页面数据队列
    dataQueue = Queue()
    # 图片资源url
    linkQueue = Queue()
    #  命名队列
    nameQueue = Queue()

    for i in range(1, int(pages)+1):
        fulurl = url + str(i)+'&_t=0'
        pageQueue.put(fulurl)

    for i in range(1, int(pages)*20):
        nameQueue.put(i)

    cThread = []
    for threadname in range(1,5):
        thread = pageCollect(pageQueue, dataQueue)
        thread.start()
        cThread.append(thread)

    pThread = []
    for threadname in range(1, 4):
        thread = contentParse(dataQueue, linkQueue)
        thread.start()
        pThread.append(thread)

    dThread = []
    for threadname in range(1, 5):
        thread = downloadPic(linkQueue, nameQueue, Dirpath)
        thread.start()
        dThread.append(thread)

    while not pageQueue.empty():
        pass

    global COLLECT_EXIT
    COLLECT_EXIT = True

    for thread in cThread:
        thread.join()

    while not dataQueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True

    for thread in pThread:
        thread.join()

    while not linkQueue.empty():
        pass

    global DOWNLOAD_EXIT
    DOWNLOAD_EXIT = True

    for thread in dThread:
        thread.join()




if __name__ == "__main__":
    print "微博图片多线程下载"
    print "仅支持单一关键词"
    print "默认保存路径为同目录下的关键字目录"
    print "=" * 60
    pages = raw_input("请输入采集页数：")
    keyword = raw_input("请输入采集关键字:")
    data = urllib.urlencode({'search': keyword})
    url = 'http://s.weibo.com/ajax/pic/list?'+data+'&page='
    Dirpath = mkDir(keyword)
    start = time.time()
    main(url, pages, Dirpath)
    end = time.time()
    print u"----用时:%.2f s----" % (end - start)

    print u"----OK----"
