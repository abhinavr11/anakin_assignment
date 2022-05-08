import requests
import urllib.parse
import sys
import json
import threading
import datetime

STARTT = datetime.datetime.now()

def scrape(lock,urls):
    
  
    head = {
    "accept-encoding":"gzip",
    "authorization":"Bearer 2de2ea56-4e3c-4401-9a76-c014c70bdc08",
    "connection":"Keep-Alive",
    "cookie":"LBI=-1941669348; inapp=true; fence=0; JSESSIONID=0B05C4127AB75E4CFED31284A948BB10",
    "device-type":"android",
    "host":"www.hktvmall.com",
    "ott-uuid":"e04d5772-cb0f-4356-acd5-96819447eb2d",
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
        products.append(requests.get(url,headers = head).json())
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
    
    lock = threading.Lock()
    global counter 
    counter = 0
    # creating threads
    #t1 = threading.Thread(target=scrape, args=(lock,product_codes[:1000]))
    #t2 = threading.Thread(target=scrape, args=(lock,product_codes[1000:2000]))
    #t3 = threading.Thread(target=scrape, args=(lock,product_codes[2000:3000]))
    #t4 = threading.Thread(target=scrape, args=(lock,product_codes[3000:4000]))

    
            # start threads
    #t1.start()
    #t2.start()

            # wait until threads finish their job
    #t1.join()
    #t2.join()

    threads = []
    for i in range(100):
        if i == 99:
            t = threading.Thread(target=scrape, args=(lock,product_codes[i*4665:-1]))
        else:
            t = threading.Thread(target=scrape, args=(lock,product_codes[i*4665:(i+1)*4665]))
        threads.append(t)
    
    [ t.start() for t in threads ]
    # wait for the threads to finish
    [ t.join() for t in threads ]