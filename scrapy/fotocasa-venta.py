#
# Crawler pisos en venta Fotocasa
# Ignacio Gallegos
#

import scrapy
import re
import json
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from scrapy.crawler import CrawlerProcess


class Piso(scrapy.Item):
    rsid = scrapy.Field()
    buildingType = scrapy.Field()
    buildingSubtype = scrapy.Field()
    clientId = scrapy.Field()
    clientUrl = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    timestamp = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    rooms = scrapy.Field()
    baths = scrapy.Field()
    surface = scrapy.Field()
    isNew = scrapy.Field()
    isNewConstruction = scrapy.Field()
    location = scrapy.Field()
    phone = scrapy.Field()
    price = scrapy.Field()
    priceRaw = scrapy.Field()
    multimedia= scrapy.Field()


class FotocasaSpider(scrapy.spiders.CrawlSpider):
    name = 'Fotocasa'
    allowed_domain = ['www.fotocasa.es']
    start_urls = ['https://www.fotocasa.es/es/comprar/viviendas/espana/todas-las-zonas/l']

    rules = {
        scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow = (), restrict_xpaths = ('//li[@class="sui-PaginationBasic-item sui-PaginationBasic-item--control"]')), callback = 'parse_item', follow = True)
    }

    def parse_item(self, response):
      script = response.xpath("/html/body/script[1]").extract()
      if (len(script) >=1):
        script = script[0]
      try:
        m = re.search('window\.__INITIAL_PROPS__ = JSON\.parse\("(.+?)"\);', script)
        if m:
          try: 
            parsedJson = json.loads(m.group(1).replace('\\"', '"'))
            for piso in parsedJson["initialSearch"]["result"]["realEstates"]:
              nuevoPiso= Piso()
              nuevoPiso['rsid'] = piso['id']
              nuevoPiso['buildingType'] = piso['buildingType']
              nuevoPiso['buildingSubtype'] = piso['buildingSubtype']
              nuevoPiso['clientId'] = piso['clientId']
              nuevoPiso['clientUrl'] = piso['clientUrl']
              nuevoPiso['latitude'] = piso['coordinates']['latitude']
              nuevoPiso['longitude'] = piso['coordinates']['longitude']
              nuevoPiso['timestamp'] = piso['date'].get('timestamp', 0)
              nuevoPiso['description'] = piso['description'].replace('\r\n', '').replace('\n','').replace(';',',').replace('\\\n','')
              nuevoPiso['url'] = piso['detail']['es-ES']
              for feature in piso['features']:
                if feature['key'] == "rooms":
                  nuevoPiso['rooms'] = feature['value']
                elif feature['key'] == "bathrooms":
                  nuevoPiso['baths'] = feature['value']
                elif feature['key'] == "surface":
                  nuevoPiso['surface'] = feature['value']
              nuevoPiso['isNew'] = piso['isNew']
              nuevoPiso['isNewConstruction'] = piso['isNewConstruction']
              nuevoPiso['location'] = piso['location']
              nuevoPiso['phone'] = piso['phone']
              nuevoPiso['price'] = piso['price']
              nuevoPiso['priceRaw'] = piso['rawPrice']
              images = ""
              for media in piso['multimedia']:
                images = images + media['src'] + '|'
              nuevoPiso['multimedia'] = images 
              yield nuevoPiso
          except Exception as ex:
            pass
      except Exception:
        pass




# optional
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'DOWNLOAD_DELAY': 0.20,
    'FEED_FORMAT': 'csv', 
    'FEED_URI': 'result.csv'
})

process.crawl(FotocasaSpider)
process.start()
