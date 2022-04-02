from aioitertools import product
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from IPython.display import clear_output
import pickle
from datetime import datetime
import json
import numpy as np



def get_links():

    
    URL = "https://www.bigbasket.com/product/all-categories/"
    req = Request(URL)
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'lxml')

    pages = []
    for divs in soup.find_all("div", {"class": "uiv2-search-category-listing-cover"}):
        for div in divs.find_all("div",{"class":"DropDownColum"}):
            for li in div.find_all("li"):
                pages.append(URL[:25]+li.find('a')['href'])
    

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    length = len(pages)
    #l2p_pg =[]  #dicts of all products on all pages of different categories
    missed_pgs = []
    product_links = []
    for idx ,pg in enumerate(pages):
        #pr_in_p = [] #list of links products in one page
        driver = webdriver.Chrome(options=chrome_options)
        try:      
            driver.get(pg)
            html = driver.page_source
            soup_pg  = BeautifulSoup(html)
        except:
            print(f"missed {pg}")
            missed_pgs.append(pg)
            continue

        driver.close()
        clear_output(wait=True)
        print(f"Scraping for links to products per category; Progress=> : {idx}/{length}")
        
        
        for prod in soup_pg.find_all("div",{"qa":"product"}):
            #pr_in_p.append(URL[:25]+prod.find('a')['href'])
            product_links.append(URL[:25]+prod.find('a')['href'])
        
        
        #l2p_pg.append({pg.split('/')[4]+"~"+pg.split('/')[5]+"~"+pg.split('/')[6] : pr_in_p})
    
    with open('missed_pages_logs.json', 'w') as outfile:
        json.dump(missed_pgs, outfile)
    outfile.close()
    return product_links

def generate_results(mode = 0, product_links = []):
    
    if len(product_links) == 0 :
        raise Exception("No links scraped")
        
    final_dict = []
    missed_products = []
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    if mode == 0 :
        parsed_soups = []
  
        for idxx,url in enumerate(product_links):
            
            try:
                req_pr = Request(url)
                webpage_pr = urlopen(req_pr).read()
                soup_pr_temp = BeautifulSoup(webpage_pr, 'lxml')
            except:
                print(f"Missed parsing page {url}")
                missed_products.append(url)
                continue
            
            parsed_soups.append(soup_pr_temp) 
            clear_output(wait=True)
            print(f"Scraping each product details; Progress=> : {idxx}/{len(product_links)}")



        for idx,soup_pr in enumerate(parsed_soups):
            name = soup_pr.find_all("h1",{"class":"GrE04"})[0].text
            currency = soup_pr.find_all("td",{"data-qa":"productPrice"})[0].text.split(' ')[0]
            img_url = soup_pr.find_all("img",{"class":"_3oKVV"})[2]['src']
            location = soup_pr.find_all("div",{"class":"_1N37e"})[0].text
            categories = soup_pr.find_all("div",{"class":"_1PBA_"})[0].text.split('>')[1:-1]
            
            address = None
            company = None
            ean = None
            country = None
            in_stock = True
            
            if soup_pr.find_all("td",{"data-qa":"productPrice"})[0].text.split(' ')[1]:
                price = float(soup_pr.find_all("td",{"data-qa":"productPrice"})[0].text.split(' ')[1])
            else:
                in_stock = False
                price = -1
            
            if len(soup_pr.find_all("a",{"context":"brandlabel"})) != 0 :
                lbl = soup_pr.find_all("a",{"context":"brandlabel"})[0].text
            else:
                lbl = 'Unknown'
            
            if len(soup_pr.find_all("div",{"class":["_26MFu","_2fn-7"]})) != 0:
                desc = soup_pr.find_all("div",{"class":["_26MFu","_2fn-7"]})[0].text
            else :
                desc = 'Unknown'
            
            if len(soup_pr.find_all("td",{"class":"_2ifWF"})) == 0:
                AP = price
            else:
                AP = float(soup_pr.find_all("td",{"class":"_2ifWF"})[0].text.split(' ')[1])
                
                
            if len(soup_pr.find_all("div",{"class":"_1q4Li"})) != 0:
                rating = float(soup_pr.find_all("div",{"class":"_1q4Li"})[0].text)
            else :
                rating = 0
            
            if len(soup_pr.find_all("div",{"class":"gmwyk"})) != 0:
                rating_count = soup_pr.find_all("div",{"class":"gmwyk"})[0].text
            else :
                rating_count = 'Not Rated'
                

            for res in soup_pr.find_all("div",{"class":["_26MFu","_2fn-7"]}):
                if 'ean code' in res.text.lower():

                    for idx_,addr in enumerate(res.text.split(':')):
                        if 'manu' in addr.lower():
                            address = res.text.split(':')[idx_+1].split('  ')[0] 
                            company = res.text.split(':')[idx_+1].split('  ')[0].split(',')[0] 
                        if 'ean code' in addr.lower():
                            ean = res.text.split(':')[idx_+1].split('  ')[0]  
                        
                        if 'origin' in addr.lower():
                            country = res.text.split(':')[idx_+1].split('  ')[0]
                
            
            discount = AP - price
            
            
            Dict = {
                    
                    "brand_name":lbl,
                    "category":categories,
                    "description":desc,
                    "discount":discount,
                    "discounted_price":price,
                    "image_url":img_url,
                    "is_instock":in_stock,
                    "item_name":name,
                    "item_url":product_links[idx],
                    "location":location,
                    "price":AP,
                    "rating":rating,
                    "review_count":rating_count,
                    "seller_address":address,
                    "seller_name":company,
                    "sku":ean,
                    "timestamp":current_time,
                    "country_code":country,
                    "unit":currency
            }
            
            final_dict.append(Dict)
            
            clear_output(wait=True)  
            print(f"Collecting info about product; Progress=> {idx}/{len(parsed_soups)}")

    else:

        for idx,url in enumerate(product_links):
            
            try:
                req_pr = Request(url)
                webpage_pr = urlopen(req_pr).read()
                soup_pr = BeautifulSoup(webpage_pr, 'lxml')
            
            except:
                print(f"Missed parsing page {url}")
                missed_products.append(url)
                continue
        
            name = soup_pr.find_all("h1",{"class":"GrE04"})[0].text
            currency = soup_pr.find_all("td",{"data-qa":"productPrice"})[0].text.split(' ')[0]
            img_url = soup_pr.find_all("img",{"class":"_3oKVV"})[2]['src']
            location = soup_pr.find_all("div",{"class":"_1N37e"})[0].text
            categories = soup_pr.find_all("div",{"class":"_1PBA_"})[0].text.split('>')[1:-1]
            
            address = None
            company = None
            ean = None
            country = None
            in_stock = True
            
            if soup_pr.find_all("td",{"data-qa":"productPrice"})[0].text.split(' ')[1]:
                price = float(soup_pr.find_all("td",{"data-qa":"productPrice"})[0].text.split(' ')[1])
            else:
                in_stock = False
                price = -1
            
            if len(soup_pr.find_all("a",{"context":"brandlabel"})) != 0 :
                lbl = soup_pr.find_all("a",{"context":"brandlabel"})[0].text
            else:
                lbl = 'Unknown'
            
            if len(soup_pr.find_all("div",{"class":["_26MFu","_2fn-7"]})) != 0:
                desc = soup_pr.find_all("div",{"class":["_26MFu","_2fn-7"]})[0].text
            else :
                desc = 'Unknown'
            
            if len(soup_pr.find_all("td",{"class":"_2ifWF"})) == 0:
                AP = price
            else:
                AP = float(soup_pr.find_all("td",{"class":"_2ifWF"})[0].text.split(' ')[1])
                
                
            if len(soup_pr.find_all("div",{"class":"_1q4Li"})) != 0:
                rating = float(soup_pr.find_all("div",{"class":"_1q4Li"})[0].text)
            else :
                rating = 0
            
            if len(soup_pr.find_all("div",{"class":"gmwyk"})) != 0:
                rating_count = soup_pr.find_all("div",{"class":"gmwyk"})[0].text
            else :
                rating_count = 'Not Rated'
                

            for res in soup_pr.find_all("div",{"class":["_26MFu","_2fn-7"]}):
                if 'ean code' in res.text.lower():

                    for idx_,addr in enumerate(res.text.split(':')):
                        if 'manu' in addr.lower():
                            address = res.text.split(':')[idx_+1].split('  ')[0] 
                            company = res.text.split(':')[idx_+1].split('  ')[0].split(',')[0] 
                        if 'ean code' in addr.lower():
                            ean = res.text.split(':')[idx_+1].split('  ')[0]  
                        
                        if 'origin' in addr.lower():
                            country = res.text.split(':')[idx_+1].split('  ')[0]
                
            
            discount = AP - price
            
            
            Dict = {
                    
                    "brand_name":lbl,
                    "category":categories,
                    "description":desc,
                    "discount":discount,
                    "discounted_price":price,
                    "image_url":img_url,
                    "is_instock":in_stock,
                    "item_name":name,
                    "item_url":product_links[idx],
                    "location":location,
                    "price":AP,
                    "rating":rating,
                    "review_count":rating_count,
                    "seller_address":address,
                    "seller_name":company,
                    "sku":ean,
                    "timestamp":current_time,
                    "country_code":country,
                    "unit":currency
            }
            
            final_dict.append(Dict)
            
            clear_output(wait=True)  
            print(f"Collecting info about product; Progress=> {idx}/{len(parsed_soups)}")

    return final_dict,missed_products
    


if __name__ == '__main__':

    product_links = get_links()
    final_result,missed_products = generate_results(mode = 0, product_links=product_links)
    
    with open('missed_products_log.json', 'w') as outfile1:
        json.dump(missed_products, outfile1)
    outfile1.close()

    with open('BigBasketData.json', 'w') as outfile2:
        json.dump(final_result, outfile2)
    outfile2.close()

