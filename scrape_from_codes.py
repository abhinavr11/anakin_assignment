import requests
import urllib.parse
import sys
import json

def scrape_using_codes():
    with open('codes.json') as json_file:
        product_codes = json.load(json_file)
        json_file.close()

    
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
    lengthp = len(product_codes)
    for i,pr_lnk in enumerate(product_codes):
        url = product_base_link+pr_lnk+"&lang=en&no_stock_redirect=true&user_id=anonymous"
        products.append(requests.get(url,headers = head).json())
        sys.stdout.write(f"\rScraping product %i /{lengthp}" % i)
        sys.stdout.flush() 
        
        if i%1000 == 0:
            with open('hktvdata.json', 'w') as outfile:
                    json.dump(products, outfile)
                    outfile.close()


if __name__ == "__main__":

    scrape_using_codes()