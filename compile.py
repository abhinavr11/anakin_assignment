import requests
import urllib.parse
import sys
import json
import threading
import datetime
import time


def compiler(products):
    items_list = []
    uniqueCatIds = set()
    uniqueCats = []
    category_list = []

    for idx,pr in enumerate(products):    
        sys.stdout.write(f"\r Writing product %i /" %idx)
        sys.stdout.flush()
        modifier_options = []
        
        if len(pr['baseOptions'][0]['options'][0]['variantOptionQualifiers']) == 0:
            pass
        else:
            for mod in pr['baseOptions'][0]['options']:  
                modifier_options.append({'name':mod['variantOptionQualifiers'][0]['name'],
                                        'price':pr['price']['value'],
                                        'option_id':mod['code'],
                                        'available':mod['stock']['stockLevelStatus']['codeLowerCase'],})
        if len(pr['priceList']) > 1 :
            discountedPrice = pr['priceList'][1]['value']
            
        else:
            discountedPrice = 'None'
            
        if 'promotionText' in pr.keys():
            promotionText = pr['promotionText']
        else:
            promotionText = 'None'
        items_list.append({
            'item_name':pr['name'],
            'item_id':pr['code'],
            'description':pr['description'],
            'available':pr['purchasable'],
            'alcohol':'None',
            'popular':str(pr['recommendPercent']>=50 and True),
            'price':pr['price']['value'],
            'price_unit':pr['price']['currencyIso'],
            'discounted_price':discountedPrice ,
            'takeaway_price':'None',
            'discounted_takeaway_price':'None',
            'image_url':pr['photosTabImages'],
            'labels':pr['labels'],
            'promotion':promotionText,
            'sort_order':'None',
            'modifier_groups':[{
                    'modifier_groups_id':'None',
                    'name':'None',
                    'max_selection_points':len(pr['baseOptions'][0]['options']),
                    'min_selection_points':'1',
                    'allow_multiple_same_item':str(pr['baseOptions'][0]['selected']['stock']['stockLevel'] > 1 and True) ,
                    'description':'None',
                    'available': str(pr['baseOptions'][0]['selected']['stock']['stockLevel'] > 0 and True),
                    'modifier_options':modifier_options
                                }]
        
            })

        for cat in pr['categories']:
            if cat['code'] in uniqueCatIds:
                continue
            else:
                uniqueCatIds.add(cat['code'])
                uniqueCats.append(cat)
                
    for cat in uniqueCats:
        item_ids = []
        for itm in products:
            for itmCat in itm['categories']:
                if itmCat['code'] == cat['code']:
                    item_ids.append(itm['code'])
        
        category_list.append( {'category_id':cat['code'],
                        'name':cat['url'].split('/')[2],
                        'description':'None',
                        'sort_order':'None',
                        'items':item_ids,
                        })

    finalJson = {'timestamp':str(datetime.datetime.now()),
    'source':'HKTV Mall App',
    'country_code':'HK',
    'restaurant_id':'1',
    'unmapped':products,
    'category': category_list,        
    'items': items_list     
            
        }

    with open('compiledHKTV.json') as fjson:
        json.dump(finalJson,fjson)
    fjson.close()



if __name__ == "__main__":
    with open('hktvdata.json') as json_file:
        products = json.load(json_file)
    json_file.close()
    
    compiler(products)
