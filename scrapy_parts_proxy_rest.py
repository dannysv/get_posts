import time
import urllib
from urllib import urlopen
from Queue import Queue
from bs4 import BeautifulSoup
import logging
from threading import Thread
import requests
from itertools import cycle
import traceback
from lxml.html import fromstring

ja = 99

def get_proxies():
    url='https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()

    #print('fsg')
    for i in parser.xpath('//*[@id="proxylisttable"]/tbody/tr'):
        #print('a')
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabing IP and corresponding port
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

proxies = get_proxies()
print(len(proxies))
proxies_f = set()

#remove 
for prox in proxies:
    try:
        tt = requests.get('http://www.iac.es/galeria/westend/node15.html', proxies={"http":prox, "https":prox}, timeout=4)
        proxies_f.add(prox)
        print('add')
    except Exception as e:
        print("no add")

proxy_pool = cycle(proxies_f)

def get_comments_pag_ifexist(q, result,cycle_proxies):
    while not q.empty():
        work = q.get()
        url = work
        #print(url)
        proxy = next(cycle_proxies)
        #proxy = first_proxy
        try:
            #a = urllib.urlopen('https://www.dailystrength.org'+url)
            a = requests.get('https://www.dailystrength.org'+url, proxies={"http":proxy, "https":proxy},timeout=20)
            soup = BeautifulSoup(a.content)
            #comments = soup.findAll("div", {"class" : "comments__item"})
            #if(len(comments)>0):
            end = soup.findAll("a", {"class": "pagination__endlink"})
            if(len(end)>0):
                parts = end[1]["href"].split('page=')
                lk = parts[0]
                last = parts[1]
                for i in range(int(last)):
                    result.append(lk+'page='+str(i))
                    print(lk+'page='+str(i+1))
            else:
                result.append(url)
                print(url)
            #else:
               # result.append(url)
                #print(url)
        except Exception as e:
            print("estoy aqui e intentare otra vez\n\n")
            print(proxy)
            #print(e)
            #first_proxy = next(cycle_proxies)
            q.put(work)
        q.task_done()
    return True

import json




#load the links
with open('post_threads_links_last.json') as f:
    data = json.load(f)

urls = data

cien_groups = [urls[(k)*3800:(k+1)*3800] for k in range(99-ja)]
cien_groups.append(urls[(99-ja)*3800:len(urls)])

#print(len(cien_groups[99]))

def process_one(index,urls_in, num_threads):
    # set up the queue to hold all the urls
    q = Queue(maxsize=0)
    print("number of urls: %s " %len(urls_in))
    pnum_threads = min(num_threads, len(urls_in))
    print("we use %s threads" %pnum_threads)
    results = []
    #
    for i in range(len(urls_in)):
        #need
        q.put(urls_in[i])
    
    ts = time.time()
    for j in range(pnum_threads):
        logging.debug('Starting thread ', j)
        worker = Thread(target = get_comments_pag_ifexist, args=(q, results, proxy_pool))
        worker.setDaemon(True)

        worker.start()

    # now wait until the queue has been processed
    q.join()

    logging.info('All tasks completed')

    #save
    with open('post_threads_links_pagination'+str(index+ja)+'.json', 'w') as out:
        json.dump(results, out)


for index,group in enumerate(cien_groups):
    print("first group ...")
    ts = time.time() 
    process_one(index, group, 50)
    tf = time.time()
    print(tf-ts)
    time.sleep(30)
