# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

import pymysql
import json
import re
import logging

class HomespiderPipeline:
    def __init__(self) -> None:
        self.sale_methods = ['negotiation', 'auction', 'tender', 'deadline_sale', 'poa', 'offers']
        self.property_types = {'house': 'house', 'apartment': 'apartment', 'unit' : 'unit', 'lifestyle_property' : 'lifestyle_dwelling', 'townhouse' : 'townhouse', 'section' : 'section', 'lifestyle_section': 'lifestyle_section', 'studio': 'studio'}
        self.ownerships = ['freehold', 'leasehold', 'cross_lease', 'unit_title', 'company_share']
        self.house_category = 'business'
        # conn = pymysql.connect(
        #     host='192.168.150.128',
        #     user='root',
        #     password='123456',
        #     database='homue_api',
        #     port=3366
        # )
        conn = pymysql.connect(
            host='homue-dev-mysql.ckdssrns2bi1.ap-southeast-2.rds.amazonaws.com',
            user='admin',
            password='gorsuj2nigpy',
            database='homue_api',
            port=3306
        )
        cursor = conn.cursor()
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

        sql = f"SELECT * FROM last_spider_houses WHERE category='{self.house_category}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        last_spider_houses = []
        for row in results:
            last_spider_houses.append(f"{row[1]}_{row[2]}")

        self.last_spider_houses = last_spider_houses

        conn.close()
        logging.info("last_spider_houses")
        logging.info(self.last_spider_houses)
        self.media_url = "https://mediaserver.realestate.co.nz"

    def process_item(self, item, spider):
        
        houseId = item['houseId']
        category = item['category']
        combin_key = f"{houseId}_{category}"
        if combin_key in self.last_spider_houses:
            raise DropItem(f"Duplicate item found: {houseId}")
            # item['is_spided'] = 1
        
        agency = item['agency']
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
        agent = item['agent']
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

        priceDisplay = item['priceDisplay']
        priceDisplay = priceDisplay.replace(' ', '_').lower()
        if priceDisplay in self.sale_methods:
            item['salesMethod'] = priceDisplay
        else:
            item['salesMethod'] = 'others'
            item['enquiryOver'] = re.findall(r'\d+', priceDisplay.replace(',', ''))

        propertyType = item['propertyType']
        if propertyType is not None:
            propertyType = propertyType.replace(' ', '_').lower()
            if propertyType in self.property_types.keys():
                item['propertyType'] = self.property_types.get(propertyType)
            else:
                pass

        if (item['ownership'] is not None) and (item['ownership'] <= 5):
            item['ownership'] = self.ownerships[item['ownership'] - 1]
        else:
            item['ownership'] = self.ownerships[4]

        openHomeTimes = item['openHomeTimes']
        newOpenHomeTimes = []
        if len(openHomeTimes) != 0:
            for openHomeTime in openHomeTimes:
                newOpenHomeTime = [openHomeTime.get('start'), openHomeTime.get('end')]
                newOpenHomeTimes.append(newOpenHomeTime)
            item['openHomeTimes'] = newOpenHomeTimes

        if item['regionName'] is not None:
            item['regionId'] = self.regions.get(item['regionName'].replace(' ', '').lower())
        if item['cityName'] is not None:
            item['cityId'] = self.cities.get(item['cityName'].replace(' ', '').lower())
        if item['districtName'] is not None:
            item['districtId'] = self.districts.get(item['districtName'].replace(' ', '').lower())
        item['otherFacilities'] = json.dumps(item['otherFacilities'])
        item['videoSrc'] = json.dumps(item['videoSrc'])
        # item['photos'] = json.dumps(item['photos'])
        item['floorPlanPhotos'] = json.dumps(item['floorPlanPhotos'])
        item['openHomeTimes'] = json.dumps(item['openHomeTimes'])
        item['primarySchool'] = json.dumps(item['primarySchool'])
        item['intermediateSchool'] = json.dumps(item['intermediateSchool'])
        item['secondarySchool'] = json.dumps(item['secondarySchool'])
        item['childCares'] = json.dumps(item['childCares'])
        item['features'] = json.dumps(item['features'])
        item['agents'] = json.dumps(item['agents'])
        item['detail_address'] = json.dumps(item['detail_address'])
        item['agency'] = json.dumps(item['agency'])
        item['agent'] = json.dumps(item['agent'])
        
        return item


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
        return item

