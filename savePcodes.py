import requests
import urllib.parse
import sys
import json
import threading
import datetime
import time

STARTT = datetime.datetime.now()
NTHREADS = 200
missedPg = []


headers = {
        "accept-encoding":"gzip",
        "authorization":"Bearer 7f83db17-7cd1-4742-b814-14dd05daed7f",
        "connection":"Keep-Alive",
        "cookie":"LBI=-1941669348; inapp=true; fence=0; JSESSIONID=7666D5240B540824DE19EFA71540EF49",
        "device-type":"android",
        "host":"www.hktvmall.com",
        "ott-uuid":"97665ca7-880e-43ce-8a11-5429d7a8a934",
        "user-agent":"okhttp/2.2.0"
    }
    
head = {
    "accept-encoding":"gzip",
    "authorization":"Bearer 7f83db17-7cd1-4742-b814-14dd05daed7f",
    "connection":"Keep-Alive",
    "cookie":"LBI=-1941669348; inapp=true; fence=0; JSESSIONID=0B05C4127AB75E4CFED31284A948BB10",
    "device-type":"android",
    "host":"www.hktvmall.com",
    "ott-uuid":"e04d5772-cb0f-4356-acd5-96819447eb2d",
    "user-agent":"okhttp/2.2.0"
    }

def getAllPageLinks():
    zones = ["thirteenlandmarks","supermarket","personalcarenhealth","beautynhealth","homenfamily","housewares","deals","sportsntravel"]
    

    all_pages = []
    all_pages_links = []
    products_page_url_base = "https://www.hktvmall.com/hktvwebservices/v1/hktv/search_products_v2?query="

    for zone in zones:
        categories = "https://www.hktvmall.com/hktvwebservices/v1/hktv/get_category_directory?lang=en&zone="+zone+"&maxLevel=3"
        cat = requests.get(categories,headers = headers).json()
        
        for category in cat['categories'] :

            if 'subcats' in category.keys():        
                for subcat1 in category['subcats']:

                    if 'subcats' in subcat1.keys():
                        for subcat2 in subcat1['subcats']:

                            if 'subcats' in subcat2.keys():                     
                                for subcat3 in subcat2['subcats']:
                                    all_pages.append(subcat3)

                            else:
                                all_pages.append(subcat2)                    
                    else:
                        all_pages.append(subcat1)
            else :
                all_pages.append(category)
        

    for pg in all_pages:
        all_pages_links.append(products_page_url_base+urllib.parse.quote(pg['query'])+"&lang=en&currentPage=0&pageSize=100000&user_id=anonymous")
    
    return all_pages_links

def saveCodes(lock,urls):

    all_products_links=[] 
    lengthpg = 2170 #len(all_pages_links)
    for i,lnk in enumerate(urls) :
        multiple_prod_pg = None
        try:
            multiple_prod_pg = requests.get(lnk,headers=headers).json()
        except: 
                lock.acquire()
                with open('missedPages.json', 'w') as outfilePg:
                    json.dump([lnk], outfilePg)
                    outfilePg.close()
                lock.release()
                continue
            


        lock.acquire()
        global counter
        counter += 1
        lock.release()

    
        for prd in multiple_prod_pg['products']:
            all_products_links.append(prd)
            sys.stdout.write(f"\rGenerating Product links %i /{lengthpg}" % counter)
            sys.stdout.flush() 
       
    
        
    product_codes = []
    for cde in all_products_links:
        product_codes.append(cde['code'])

    lock.acquire()
    with open('codes1.json', 'w') as outfile:
            json.dump(product_codes, outfile)
            outfile.close()
    lock.release()    
   


if __name__ == "__main__":
    apl = getAllPageLinks()
    
    lock = threading.Lock()
    global counter 
    counter = 0
    

    threads = []
    for i in range(NTHREADS):
        if i == NTHREADS-1:
            t = threading.Thread(target=saveCodes, args=(lock,apl[i*2170//NTHREADS:-1]))
        else:
            t = threading.Thread(target=saveCodes, args=(lock,apl[i*2170//NTHREADS:(i+1)*2170//NTHREADS]))
        threads.append(t)
    
    [ t.start() for t in threads ]
    # wait for the threads to finish
    [ t.join() for t in threads ]
    