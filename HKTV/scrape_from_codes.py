import requests
import urllib.parse
import sys
import json
import threading
import datetime

STARTT = datetime.datetime.now()
NTHREADS = 100

def scrape(lock,urls):
    
  
    head =  {
    "accept-encoding":"gzip",
    "authorization":"Bearer f54b14d1-2cea-47e2-b044-6d246b2d61c0",
    "connection":"Keep-Alive",
    "cookie":"LBI=-1941669348; inapp=true; fence=0; JSESSIONID=CB71E843B568BCE2091958BBA587F17A",
    "device-type":"android",
    "host":"www.hktvmall.com",
    "ott-uuid":"13542dde-009b-46ab-b3a9-fa1e256ce33b",
    "user-agent":"okhttp/2.2.0"
}


    product_base_link = "https://www.hktvmall.com/hktvwebservices/v1/hktv/get_product?product_id="
    products = []
    lengthp = 466532 #len(product_codes)
    for i,pr_lnk in enumerate(urls):
        
        lock.acquire()
        global counter
        counter += 1
        lock.release()
        
        url = product_base_link+pr_lnk+"&lang=en&no_stock_redirect=true&user_id=anonymous"
        #pr = None
        try :
            pr = requests.get(url,headers = head).json()
        except:
            lock.acquire()
            with open('missedProducts.json', 'w') as outfilePr:
                    json.dump(url, outfilePr)
                    outfilePr.close()
            lock.release()
            continue
        
        products.append(pr)
        sys.stdout.write(f"\rScraping product %i /{lengthp} Time elapsed {datetime.datetime.now()-STARTT}" % counter)
        sys.stdout.flush() 
        
        if counter % 1000 == 0:
            lock.acquire()
            with open('hktvdata.json', 'w') as outfile:
                    json.dump(products, outfile)
                    outfile.close()
            lock.release()

if __name__ == "__main__":
    with open('codes.json') as json_file:
        product_codes = json.load(json_file)
    json_file.close()
    
    product_codes = list(set(product_codes)) 
    
    lock = threading.Lock()
    global counter 
    counter = 0
    

    threads = []
    for i in range(NTHREADS):
        if i == NTHREADS-1:
            t = threading.Thread(target=scrape, args=(lock,product_codes[i*466532//NTHREADS:-1]))
        else:
            t = threading.Thread(target=scrape, args=(lock,product_codes[i*466532//NTHREADS:(i+1)*466532//NTHREADS]))
        threads.append(t)
    
    [ t.start() for t in threads ]
    # wait for the threads to finish
    [ t.join() for t in threads ]