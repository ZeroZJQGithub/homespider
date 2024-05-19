# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from datetime import datetime

import pymysql
import json
import re
import logging
import uuid

item_images_path = []

class HomespiderPipeline:
    def __init__(self, spider_category, spider_region, max_unsold_house_id, db_settings=None) -> None:
        self.sale_methods = ['negotiation', 'auction', 'tender', 'deadline_sale', 'poa', 'offers']
        self.homue_sale_methods = ['negotiation', 'auction', 'tender', 'deadline_sale', 'asking_price', 'enquiries_over']
        self.property_types = {'house': 'house', 'apartment': 'apartment', 'unit' : 'unit', 'lifestyle_property' : 'lifestyle_dwelling', 'townhouse' : 'townhouse', 'section' : 'section', 'lifestyle_section': 'lifestyle_section', 'studio': 'studio'}
        self.ownerships = ['freehold', 'leasehold', 'cross_lease', 'unit_title', 'company_share']
        self.spider_category = spider_category
        self.spider_region = spider_region
        self.max_unsold_house_id = max_unsold_house_id
        self.insert_data_items = []
        self.item_data_count = 0
        self.media_url = "https://mediaserver.realestate.co.nz"
        self.db_settings = db_settings
        logging.info(self.db_settings)

    @classmethod
    def from_crawler(cls, crawler):
        db_settings={
            'DB_HOST': crawler.settings.get('DB_HOST'),
            'DB_USER': crawler.settings.get('DB_USER'),
            'DB_PASSWORD': crawler.settings.get('DB_PASSWORD'),
            'DB_DATABASE': crawler.settings.get('DB_DATABASE'),
            'DB_PORT': crawler.settings.get('DB_PORT')
        }
        return cls(crawler.spider.spider_category, 
                   crawler.spider.spider_region, 
                   crawler.spider.max_unsold_house_id,
                   db_settings
                   )


    def open_spider(self, spider):
        # self.conn = pymysql.connect(
        #     host='192.168.150.128',
        #     user='root',
        #     password='123456',
        #     database='homue_api',
        #     port=3366
        # )
        # self.conn = pymysql.connect(
        #     host='homue-dev-mysql.ckdssrns2bi1.ap-southeast-2.rds.amazonaws.com',
        #     user='admin',
        #     password='gorsuj2nigpy',
        #     database='homue_api',
        #     port=3306
        # )
        self.conn = pymysql.connect(
            host=self.db_settings.get('DB_HOST'), 
            user=self.db_settings.get('DB_USER'), 
            password=self.db_settings.get('DB_PASSWORD'), 
            database=self.db_settings.get('DB_DATABASE'), 
            port=self.db_settings.get('DB_PORT')            
        )
        cursor = self.conn.cursor()
        sql = "SELECT * FROM nz_region"
        cursor.execute(sql)
        results = cursor.fetchall()
        nz_regions = {}
        for row in results:
            nz_regions[row[1].replace(' ', '').lower()] = row[0]
        
        self.regions = nz_regions

        sql = "SELECT * FROM nz_city"
        cursor.execute(sql)
        results = cursor.fetchall()
        nz_cities = {}
        for row in results:
            nz_cities[row[2].replace(' ', '').lower()] = row[0]

        self.cities = nz_cities

        sql = "SELECT * FROM nz_district"
        cursor.execute(sql)
        results = cursor.fetchall()
        nz_districts = {}
        for row in results:
            nz_districts[row[2].replace(' ', '').lower()] = row[0]

        self.districts = nz_districts

        # sql = f"SELECT * FROM last_spider_houses WHERE category='{self.spider_category}'"
        # cursor.execute(sql)
        # results = cursor.fetchall()
        # last_spider_houses = []
        # for row in results:
        #     last_spider_houses.append(f"{row[1]}_{row[2]}")

        # self.last_spider_houses = last_spider_houses
        # sql = f"SELECT house_id FROM homue_import_houses WHERE category='{self.spider_category}' AND slugRegion='{self.spider_region}' ORDER BY house_id DESC LIMIT 1"
        # cursor = self.conn.cursor()
        # cursor.execute(sql)
        # result = cursor.fetchone()
        # self.max_unsold_house_id = result[0]
        
        cursor.close()
        # self.conn.close()

    def close_spider(self, spider):
        if len(self.insert_data_items) == 0:
            self.insert_images_to_database()
            self.conn.close()
        else:
            self.insert_items_to_database(self.insert_data_items)
            self.conn.close()

    def process_item(self, item, spider):
        houseId = item['houseId']
        if houseId <= self.max_unsold_house_id:
            raise DropItem(f"Aleardy crawl the house: {houseId}")
        else:        
            agency = item.get('agency')
            if agency is not None:
                if agency.get('image-base-url') is not None:
                    agency_logo = {
                        'office-logo': self.media_url + agency.get('image-base-url') + '.scale.x40.jpg'
                    }
                else:
                    agency_logo = {
                        'office-logo': ""
                    }
                agency.update(agency_logo)
                item['agency'] = agency
            else:
                item['agency'] = []

            agent = item.get('agent')
            if agent is not None:
                if agent.get('image') is not None:
                    agent_avatar = {
                        'avatar': self.media_url + agent.get('image').get('base-url') + '.fcrop.900x900.jpg'
                    }
                else:
                    agent_avatar = {
                        'avatar': ""
                    }
                agent.update(agent_avatar)
                item['agent'] = agent
            else:
                item['agent'] = []


            priceCode = item.get('priceCode')
            priceDisplay = item.get('priceDisplay')
            priceDisplay = priceDisplay.replace(' ', '_').lower()
            if priceCode == 1 or priceCode == 8:
                item['salesMethod'] = 'asking_price'
                item['askingPrice'] = re.findall(r'\d+', priceDisplay.replace(',', ''))[0]
            elif priceCode == 4:
                item['salesMethod'] = 'tender'
            elif priceCode == 11 or priceCode == 13:
                item['salesMethod'] = 'enquiries_over'
                item['enquiriesOver'] = re.findall(r'\d+', priceDisplay.replace(',', ''))[0]
            elif priceCode == 15:
                item['salesMethod'] = 'negotiation'
                item['negotiableFrom'] = re.findall(r'\d+', priceDisplay.replace(',', ''))[0]
            elif priceCode == 16:
                item['salesMethod'] = 'tender'
                item['tenderOffersOver'] = re.findall(r'\d+', priceDisplay.replace(',', ''))[0]
            else:
                if priceDisplay in self.sale_methods:
                    item['salesMethod'] = priceDisplay
                else:
                    item['salesMethod'] = None
            
            # priceDisplay = priceDisplay.replace(' ', '_').lower()
            # if priceDisplay in self.sale_methods:
            #     if priceDisplay in self.homue_sale_methods:
            #         item['salesMethod'] = priceDisplay
            #     else:
            #         item['salesMethod'] = 'others'
            # else:
            #     item['salesMethod'] = 'asking_price'
            #     item['enquiryOver'] = re.findall(r'\d+', priceDisplay.replace(',', ''))[0]

            # propertyType = item.get('propertyType')
            # if propertyType is not None:
            #     propertyType = propertyType.replace(' ', '_').lower()
            #     if propertyType in self.property_types.keys():
            #         item['propertyType'] = self.property_types.get(propertyType)
            #     else:
            #         pass

            if (item.get('ownership') is not None) and (item['ownership'] <= 5):
                item['ownership'] = self.ownerships[item['ownership'] - 1]

            openHomeTimes = item.get('openHomeTimes', [])
            newOpenHomeTimes = []
            if len(openHomeTimes) != 0:
                for openHomeTime in openHomeTimes:
                    newOpenHomeTime = [openHomeTime.get('start'), openHomeTime.get('end')]
                    newOpenHomeTimes.append(newOpenHomeTime)
                item['openHomeTimes'] = newOpenHomeTimes

            if item.get('regionName') is not None:
                item['regionId'] = self.regions.get(item['regionName'].replace(' ', '').lower())
            else:
                item['regionId'] = 0

            if item.get('cityName') is not None:
                item['cityId'] = self.cities.get(item['cityName'].replace(' ', '').lower())
            else:
                item['cityId'] = 0   

            if item.get('districtName') is not None:
                item['districtId'] = self.districts.get(item['districtName'].replace(' ', '').lower())
            else:
                item['districtId'] = 0    

            if item.get('hasSwimmingPool') == 'true':
                item['amenities'] = 'swimming_pool'  

            if item.get('capitalValue') is not None:
                item['capitalValueUnavailable'] = 1
            else:
                item['capitalValueUnavailable'] = 0  

            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_at'] = created_at      
            videoSrcs = item.get('videoSrc', [])
            if (videoSrcs is not None) and (len(videoSrcs) > 0):
                item['videoSrc'] = videoSrcs[0].get('url')
            else:
                item['videoSrc'] = None
            item['otherFacilities'] = json.dumps(item.get('otherFacilities', []))
            # item['videoSrc'] = json.dumps(item['videoSrc'])
            item['floorPlanPhotos'] = json.dumps(item.get('floorPlanPhotos', []))
            item['openHomeTimes'] = json.dumps(item.get('openHomeTimes', []))
            item['primarySchool'] = json.dumps(item.get('primarySchool', []))
            item['intermediateSchool'] = json.dumps(item.get('intermediateSchool', []))
            item['secondarySchool'] = json.dumps(item.get('secondarySchool', []))
            item['childCares'] = json.dumps(item.get('childCares', []))
            # item['features'] = json.dumps(item['features'])
            item['agents'] = json.dumps(item.get('agents', []))
            item['detail_address'] = json.dumps(item.get('detail_address', []))
            item['agency'] = json.dumps(item.get('agency', []))
            item['agent'] = json.dumps(item.get('agent', []))

            self.process_insert_data(item)
            if self.item_data_count == 100:
                self.insert_items_to_database(self.insert_data_items)
            return item

    def process_insert_data(self, item):
        is_new_insert = 1
        landArea = float(item.get('landArea')) if item.get('landArea') is not None else 0.00
        landArea = landArea * 10000 if item.get('landAreaUnit') == 'HA' else landArea
        floorArea = float(item.get('floorArea')) if item.get('floorArea') is not None else 0.00
        floorArea = floorArea * 10000 if item.get('floorAreaUnit') == 'ha' else floorArea
        regionId = int(item.get('regionId')) if item.get('regionId') is not None else 0
        cityId = int(item.get('cityId')) if item.get('cityId') is not None else 0
        districtId = int(item.get('districtId')) if item.get('districtId') is not None else 0
        enquiriesOver = float(item.get('enquiryOver')) if item.get('enquiryOver') is not None else 0.00
        expectedSalePrice = float(item.get('expectedSalePrice')) if item.get('expectedSalePrice') is not None else 0.00
        negotiableFrom = float(item.get('negotiableFrom')) if item.get('negotiableFrom') is not None else 0.00
        askingPrice = float(item.get('askingPrice')) if item.get('askingPrice') is not None else 0.00
        capitalValue = float(item.get('capitalValue')) if item.get('capitalValue') is not None else 0.00
        tenderOffersOver = float(item.get('tenderOffersOver')) if item.get('tenderOffersOver') is not None else 0.00
        buildingAge = int(item.get('buildingAge')) if item.get('buildingAge') is not None else 0

        insert_data = (uuid.uuid4().hex, item.get('houseId'), item.get('title'), item.get('url'), item.get('listing_no'), item.get('category'), regionId, item.get('regionName'), cityId, item.get('cityName'),
                       districtId, item.get('districtName'), item.get('unitNumber'), item.get('streetNumber'), item.get('streetName'), item.get('slugRegion'), item.get('propertyType'), item.get('ownership'), item.get('salesMethod'), enquiriesOver,
                       item.get('auctionTime'), item.get('tenderTime'), item.get('deadlineTime'), item.get('openHomeTimes'), landArea, floorArea, item.get('bedrooms'), item.get('bathrooms'), item.get('garageParking'), expectedSalePrice, 
                       item.get('offStreetParking'), buildingAge, item.get('otherFacilities'), item.get('englishDescription'), item.get('primarySchool'), item.get('intermediateSchool'), item.get('secondarySchool'), item.get('childCares'), item.get('floorPlanPhotos'), item.get('videoSrc'), 
                       item.get('latitude'), item.get('longtitude'), item.get('address'), item.get('agent'), item.get('agents'), item.get('agency'), item.get('auctionAddress'), item.get('detail_address'), capitalValue, item.get('subtitle'), 
                       item.get('pubished_date'), is_new_insert, json.dumps(item.get('photos')), item.get('amenities'), negotiableFrom, askingPrice, tenderOffersOver, item.get('landAreaUnit'), item.get('floorAreaUnit'), item.get('capitalValueUnavailable'),
                       item.get('priceDisplay'), item.get('priceCode'), item.get('propertyShortId'), item.get('created_at')
                    )        
        self.insert_data_items.append(insert_data)
        self.item_data_count += 1

    def insert_items_to_database(self, insert_data):
        sql = "INSERT INTO homue_import_houses(house_id, origin_house_id, title, url, listing_no, category, regionId, regionName, cityId, cityName, " + \
              "districtId, districtName, unitNumber, streetNumber, streetName, slugRegion, propertyType, ownership, salesMethod, enquiriesOver, " + \
              "auctionTime, tenderTime, deadlineTime, openHomeTimes, landArea, floorArea, bedrooms, bathrooms, garageParking, expectedSalePrice, " + \
              "offStreetParking, buildingAge, otherFacilities, englishDescription, primarySchool, intermediateSchool, secondarySchool, childCares, floorPlanPhotos, videoSrc, " + \
              "latitude, longtitude, address, agent, agents, agency, auctionAddress, detail_address, capitalValue, subtitle, " + \
              "pubished_date, is_new_insert, photos, amenities, negotiableFrom, askingPrice, tenderOffersOver, landAreaUnit, floorAreaUnit, capitalValueUnavailable, " + \
              "priceDisplay, priceCode, propertyShortId, created_at" + \
              ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " + \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " + \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " + \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " + \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " + \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " + \
              "%s, %s, %s, %s)"
        cursor = self.conn.cursor()
        cursor.executemany(sql, insert_data)
        self.conn.commit()

        global item_images_path
        if len(item_images_path) != 0:
            for image_path in item_images_path:
                sql = "UPDATE homue_import_houses SET image_paths=%s WHERE origin_house_id=%s"
                cursor.execute(sql, (image_path[1], image_path[0]))
                self.conn.commit()
            item_images_path.clear()

        cursor.close()
        self.insert_data_items.clear()
        self.item_data_count = 0

    def insert_images_to_database(self):
        global item_images_path
        if len(item_images_path) != 0:
            cursor = self.conn.cursor()
            for image_path in item_images_path:
                sql = "UPDATE homue_import_houses SET image_paths=%s WHERE origin_house_id=%s"
                cursor.execute(sql, (image_path[1], image_path[0]))
                self.conn.commit()
            cursor.close()
            item_images_path.clear()        


class HomeImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        # return super().file_path(request, response, info, item=item)
        image_name = request.url.split("/")[-1]
        return image_name

    def get_media_requests(self, item, info):
        realestate_header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"}
        photos = item['photos']
        for photo in photos:
            image_url = photo.get('url')
            yield scrapy.Request(url=image_url, headers=realestate_header)
    
    def item_completed(self, results, item, info):
        # return super().item_completed(results, item, info)
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter['image_paths'] = json.dumps(image_paths)

        item['photos'] = json.dumps(item['photos'])
        global item_images_path
        item_images_path.append((adapter['houseId'], adapter['image_paths']))
        return item



