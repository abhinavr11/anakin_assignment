import requests
import urllib.parse
import sys
import json

def scrape():
    zones = ["thirteenlandmarks","supermarket","personalcarenhealth","beautynhealth","homenfamily","housewares","deals","sportsntravel"]
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

    all_products_links = []
    lengthpg = len(all_pages_links)
    for i,lnk in enumerate(all_pages_links) :
        multiple_prod_pg = requests.get(lnk,headers=headers).json()
        
        for prd in multiple_prod_pg['products']:
            all_products_links.append(prd)
            sys.stdout.write(f"\rGenerating Product links %i /{lengthpg}" % i)
            sys.stdout.flush() 

    product_codes = []
    for cde in all_products_links:
        product_codes.append(cde['code'])

    product_codes = list(set(product_codes))    

    product_base_link = "https://www.hktvmall.com/hktvwebservices/v1/hktv/get_product?product_id="
    products = []
    lengthp = len(product_codes)
    for i,pr_lnk in enumerate(product_codes):
        url = product_base_link+pr_lnk+"&lang=en&no_stock_redirect=true&user_id=anonymous"
        products.append(requests.get(url,headers = head).json())
        sys.stdout.write(f"\rScraping product %i /{lengthp}" % i)
        sys.stdout.flush() 

    with open('hktvdata.json', 'w') as outfile:
        json.dump(products, outfile)
        outfile.close()


if __name__ == "__main__":
    scrape()
