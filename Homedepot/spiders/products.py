import scrapy, json, csv

from scrapy.utils.python import without_none_values
from ..utils import get_itemIds, get_zipcodes, homedepot_price_post, timestamp, get_headers


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['www.homedepot.com']
    start_url = 'https://www.homedepot.com/'
    headers = get_headers()

    filename = 'Homedepot.csv'
    results = []

    def start_requests(self):
        zipcodes = get_zipcodes()
        for zip in zipcodes:
            url = f'https://www.homedepot.com/StoreSearchServices/v2/storesearch?address={zip}&radius=50'
            yield scrapy.Request(url)

    def parse(self, response):
        data = json.loads(response.text)
        if 'stores' in data:
            stores = data['stores']
            store_id = stores[0]['storeId']
            store_name = stores[0]['name']
            store_zip = stores[0]['address']['postalCode']
            meta = {'cookiejar':store_id, 'Store_Name' : store_name, 'Store_Zip' : store_zip}

            itemsIds = get_itemIds()
            
            for itemId in itemsIds:
                url = 'https://www.homedepot.com/product-information/model?opname=productClientOnlyProduct'
                body = homedepot_price_post()
                body['variables']['itemId'], body['variables']['storeId'], body['variables']['zipCode']  = itemId, store_id, store_zip
                yield scrapy.Request(url, method='POST', body=json.dumps(body), headers=self.headers, meta=meta, callback=self.parse_product)
            
    def parse_product(self, response):
        body = json.loads(response.request.body)
        itemId = body['variables']['itemId']
        
        data = json.loads(response.text)
        product = data['data']['product']
        pr_name = product['identifiers']['productLabel']
        pr_url = product['identifiers']['canonicalUrl']
        if pr_url:
            pr_url = 'https://www.homedepot.com' + pr_url
        price = product['pricing']['value']
        price = '$' + str(price) if price else 'NA'

        result = {
            'Internet #' : itemId,
            'Product Name' : pr_name,
            'Price' : price,
            'Zip Code' : response.meta['Store_Zip'],
            'Store Name' : response.meta['Store_Name'],
            'Source' : 'Homedepot',
            'Date/Time of Extraction' : timestamp(),
            'Product URL' : pr_url
        }
        self.results.append(result)
        print(result)
        #yield result
        #return result

    def closed(self, response):
        fieldnames = ['Internet #', 'Product Name','Price','Zip Code','Store Name','Source','Date/Time of Extraction','Product URL']
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        
 

   