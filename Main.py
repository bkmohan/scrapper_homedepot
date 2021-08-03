from scrapy.crawler import CrawlerProcess
from Homedepot.spiders.products import ProductsSpider
#from scrapy.utils.project import get_project_settings


settings = {
    'BOT_NAME' : 'Homedepot',
    'SPIDER_MODULES' : ['Homedepot.spiders'],
    'NEWSPIDER_MODULE' : 'Homedepot.spiders',
    'ROBOTSTXT_OBEY' : False,
    'LOG_LEVEL' : 'ERROR',
}

print('Starting Scrapper')
process = CrawlerProcess(settings)

process.crawl(ProductsSpider)
process.start()

print('Completed')

