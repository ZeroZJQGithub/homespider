import scrapy
from scrapy import Request
from ..items import HomespiderItem
from urllib import parse
import json
from scrapy.utils.defer import maybe_deferred_to_future
from twisted.internet.defer import DeferredList
import logging
import pymysql

class HomeDefferredSpider(scrapy.Spider):
    name = "home_defferred"
    allowed_domains = ["realestate.co.nz", "platform.realestate.co.nz"]
    
    realestate_header = {"Accept": "application/json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
     # nz_regions_size = 21
    nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
    # nz_regions = ['pacific-islands', 'gisborne']
    house_categories = ['residential', 'commercial', 'rural', 'business']

    start_urls = ["https://www.realestate.co.nz/residential/sale?by=latest"]
    root_url = "https://www.realestate.co.nz"
    media_url = "https://mediaserver.realestate.co.nz"

    #example: https://platform.realestate.co.nz/search/v1/listings/42501188?include=agents,offices
    attributes_base_url = "https://platform.realestate.co.nz/search/v1/listings/"
    attributes_url_params = "agents,offices"

    #example: https://platform.realestate.co.nz/search/v1/schools?filter[geocode]=172.6241458173,-43.519763296246&filter[includeNearby]=true&page[responseType]=no-geo&page[limit]=30
    schools_base_url = "https://platform.realestate.co.nz/search/v1/schools?" 

    #example: https://platform.realestate.co.nz/search/v1/properties/z10wnbw6c
    properties_base_url = "https://platform.realestate.co.nz/search/v1/properties/"

    #example: https://platform.realestate.co.nz/search/v1/childcares?filter[ids][]=bbbbbbs0c&filter[ids][]=bbbbbbyxc&filter[ids][]=bbbbbbXyc&filter[ids][]=bbbbbb20c&filter[ids][]=bbbbbbryc&filter[ids][]=bbbbbbb0c&filter[ids][]=bbbbbbvxc&filter[ids][]=bbbbbbQvc&filter[ids][]=bbbbbbP4&filter[ids][]=bbbbbbKxc&filter[ids][]=bbbbbbHwc&filter[ids][]=bbbbbbm0c&filter[ids][]=bbbbbbl0c&filter[ids][]=bbbbbbBwc&filter[ids][]=bbbbbbPzc&filter[ids][]=bbbbbbP1c&filter[ids][]=bbbbbbKwc&filter[ids][]=bbbbbbBxc&filter[ids][]=bbbbbbg5&filter[ids][]=bbbbbb0wc&filter[ids][]=bbbbbb5wc&filter[ids][]=bbbbbbZwc&filter[ids][]=bbbbbbLyc&filter[ids][]=bbbbbbnxc&filter[ids][]=bbbbbbR4&filter[ids][]=bbbbbbr0c&filter[ids][]=bbbbbbz0c&filter[ids][]=bbbbbbFwc&filter[ids][]=bbbbbbf5&filter[ids][]=bbbbbbxxc&page[limit]=30
    childcares_base_url = "https://platform.realestate.co.nz/search/v1/childcares?"

    latest_request_page = 1

    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.spider_url = url
        urls = url.split('/')
        self.spider_category = urls[3]
        self.spider_region = urls[-1].split('?')[0]

        self.conn = pymysql.connect(
            host='192.168.150.128',
            user='root',
            password='123456',
            database='homue_api',
            port=3366
        )
        sql = f"SELECT MAX(origin_house_id) as max_house_id FROM homue_import_houses WHERE category='{self.spider_category}' AND slugRegion='{self.spider_region}'"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result[0] is not None:
            self.max_unsold_house_id = result[0]
        else:
            self.max_unsold_house_id = ''
        cursor.close()
        self.conn.close()

        self.has_smaller_house_id = False

    def start_requests(self):
        yield Request(url=self.spider_url, headers=self.realestate_header, callback=self.parse)

    def parse(self, response):
        # if self.spider_category == 'business':
        #     for house in response.css('div.listing-tile'):
        #         detail_page_link = house.css("div.tile--body>div.relative:last-child>a::attr(href)").get()
        #         if detail_page_link is not None:
        #             house_id = detail_page_link.split("/")[1]
        #             if house_id <= self.max_unsold_house_id:
        #                 pass
        #             else:
        #                 attributes_api_url = self.attributes_base_url + house_id + '?include=' + parse.quote(self.attributes_url_params)
        #                 yield Request(attributes_api_url, headers=self.realestate_header, callback=self.parse_detail)
        # else:
        #     for house in response.css('div.listing-tile'):
        #         detail_page_link = house.css('div.tile--body>div.relative:last-child>a::attr(href)').get()
        #         if detail_page_link is not None:
        #             house_id = detail_page_link.split("/")[1]
        #             if house_id <= self.max_unsold_house_id:
        #                 pass
        #             else:
        #                 attributes_api_url = self.attributes_base_url + house_id + '?include=' + parse.quote(self.attributes_url_params)
        #                 yield Request(attributes_api_url, headers=self.realestate_header, callback=self.parse_detail)
        for house in response.css('div.listing-tile'):
            detail_page_link = house.css("div.tile--body>div.relative:last-child>a::attr(href)").get()
            if detail_page_link is not None:
                house_id = detail_page_link.split("/")[1]
                logging.info(f"current house id: {house_id}")
                logging.info(f"max unsold house id: {self.max_unsold_house_id}")
                if house_id <= self.max_unsold_house_id:
                    self.has_smaller_house_id = True
                else:
                    attributes_api_url = self.attributes_base_url + house_id + '?include=' + parse.quote(self.attributes_url_params)
                    yield Request(attributes_api_url, headers=self.realestate_header, callback=self.parse_detail)

        if self.has_smaller_house_id == True:
            pass
        else:
            next_page = response.css('div.paginated-items>div.paginated-items__control:last-child a').get()
            if next_page is not None:
                self.latest_request_page = self.latest_request_page + 1
                next_page_url = f'{self.root_url}/{self.spider_category}/sale/{self.spider_region}?by=latest&page={self.latest_request_page}'
                # logging.info(next_page_url)
                yield Request(url=next_page_url, headers=self.realestate_header, callback=self.parse)
    
    async def parse_detail(self, response):
        json_data = json.loads(response.text)
        data = json_data.get('data')
        house_attributes = data.get('attributes')
        detail_address = house_attributes.get('address')
        included_data = json_data.get('included')
        full_address = detail_address.get('full-address')
        house_item = HomespiderItem()
        house_item['url'] = house_attributes.get('website-full-url')
        house_item['houseId'] = data.get('id')
        house_item['category'] = self.spider_category
        house_item['propertyType'] = house_attributes.get('listing-sub-type')
        house_item['ownership'] = house_attributes.get('title-type')
        house_item['openHomeTimes'] = house_attributes.get('open-homes')
        house_item['regionName'] = detail_address.get('region')
        house_item['cityName'] = detail_address.get('district')
        house_item['districtName'] = detail_address.get('suburb')
        house_item['unitNumber'] = detail_address.get('unit-number')
        house_item['streetNumber'] = detail_address.get('street-number')
        house_item['streetName'] = detail_address.get('street')
        house_item['title'] = full_address if len(full_address) != 0 else house_attributes.get('header')
        house_item['englishDescription'] = house_attributes.get('description')
        house_item['landArea'] = house_attributes.get('land-area')
        house_item['landAreaUnit'] = house_attributes.get('land-area-unit')
        house_item['floorArea'] = house_attributes.get('floor-area')
        house_item['floorAreaUnit'] = house_attributes.get('floor-area-unit')
        house_item['bedrooms'] = house_attributes.get('bedroom-count')
        house_item['bathrooms'] = house_attributes.get('bathroom-count')        
        house_item['listing_no'] = house_attributes.get('listing-no')
        house_item['garageParking'] = house_attributes.get('parking-garage-count')
        house_item['offStreetParking'] = house_attributes.get('parking-covered-count') 
        house_item['hasSwimmingPool'] = house_attributes.get('has-swimming-pool')
        house_item['priceDisplay'] = house_attributes.get('price-display')
        house_item['priceCode'] = house_attributes.get('price-code')
        house_item['auctionTime'] = house_attributes.get('auction-time')
        house_item['auctionAddress'] = house_attributes.get('auction-location')
        house_item['tenderTime'] = house_attributes.get('tender-date')
        house_item['deadlineTime'] = house_attributes.get('deadline-date')
        house_item['otherFacilities'] = house_attributes.get('other-features')  
        house_item['videoSrc'] = house_attributes.get('videos')
        house_item['latitude'] = detail_address.get('latitude')
        house_item['longtitude'] = detail_address.get('longitude')
        house_item['address'] = full_address
        house_item['subtitle'] = house_attributes.get('header')
        # house_item['features'] = house_attributes.get('features')
        house_item['detail_address'] = detail_address
        house_item['slugRegion'] = self.spider_region

        agents = []
        for item in included_data:
            if item['type'] == 'agent':
                agents.append(item)
                if len(agents) == 1:
                    house_item['agent'] = item.get('attributes')
            else:
                house_item['agency'] = item.get('attributes')

        house_item['agents'] = agents
        house_item['pubished_date'] = house_attributes.get('published-date')

        photos = []
        for photo_item in house_attributes['photos']:
            photo_url = self.media_url + photo_item['base-url'] + '.jpg'
            photo = {"original_name": "", "url": photo_url}
            photos.append(photo)
        house_item['photos'] = photos

        floorPlanPhotos = []
        # logging.info(house_attributes.get('floorplans'))
        if len(house_attributes.get('floorplans')) != 0:
            for photo_item in house_attributes.get('floorplans'):
                photo = {"original_name": "", "url": photo_item.get('url')}
                floorPlanPhotos.append(photo)
        house_item['floorPlanPhotos'] = floorPlanPhotos


        propertyShortId = house_attributes.get('property-short-id')
        house_item['propertyShortId'] = propertyShortId

        if detail_address.get('geopoint') != "":
            schools = house_attributes.get('schools')
            if len(schools) != 0:
                schools_params = {
                    'filter[geocode]': f"{detail_address.get('longitude')},{detail_address.get('latitude')}",
                    'filter[includeNearby]': 'true',
                    'page[responseType]': 'no-geo',
                    'page[limit]': 50
                }
                schools_url = self.schools_base_url + parse.urlencode(schools_params)
                schools_request = Request(url=schools_url, headers=self.realestate_header)
                schools_deferred = self.crawler.engine.download(schools_request)
                schools_response = await maybe_deferred_to_future(schools_deferred)
                if schools_response is not None:
                    schools_json_data = json.loads(schools_response.text)
                    schools_data = schools_json_data['data']
                    primarySchool = []
                    intermediateSchool = []
                    secondarySchool = []
                    for school in schools_data:
                        school_attributes = school.get('attributes')
                        organization_type = school_attributes.get('organization-type')
                        school_data = {
                            'organization_name': school_attributes.get('organization-name'),
                            'coed_status': school_attributes.get('coed-status'),
                            'geo_radius': school_attributes.get('geo-radius'),
                            'in_zone': school_attributes.get('in-zone'),
                            'eqi': school_attributes.get('eqi'),
                            'organization_type': organization_type,
                            'address': school_attributes.get('address'),
                            'origin_attributes': school_attributes
                        }
                        if 'Primary' in organization_type:
                            primarySchool.append(school_data)
                        elif 'Intermediate' in organization_type:
                            intermediateSchool.append(school_data)
                        else:
                            secondarySchool.append(school_data)

                    house_item['primarySchool'] = primarySchool
                    house_item['intermediateSchool'] = intermediateSchool
                    house_item['secondarySchool'] = secondarySchool                  

            child_cares = house_attributes.get('child-cares')
            if child_cares is not None:
                child_cares_params = ''
                for child_care in child_cares:
                    child_cares_params += f"filter[ids][]={child_care.get('short-id')}&"

                child_cares_params += 'page[limit]=50'
                child_cares_params = child_cares_params.replace('[', '%5B').replace(']', '%5D')
                child_cares_url = self.childcares_base_url + child_cares_params
                child_cares_request = Request(url=child_cares_url, headers=self.realestate_header)
                child_cares_deferred = self.crawler.engine.download(child_cares_request)
                child_cares_response = await maybe_deferred_to_future(child_cares_deferred)
                child_cares_json_data = json.loads(child_cares_response.text)
                child_cares_data = child_cares_json_data['data']
                house_item['childCares'] = child_cares_data 
        

        if propertyShortId is not None:
            property_url = self.properties_base_url + propertyShortId
            property_request = Request(url=property_url, headers=self.realestate_header)
            property_deferred = self.crawler.engine.download(property_request)
            property_response = await maybe_deferred_to_future(property_deferred)
            property_json_data = json.loads(property_response.text)
            properties_data = property_json_data['data']
            if properties_data is not None:
                council_information = properties_data.get('attributes').get('council-information')
                if council_information is not None:
                    house_item['capitalValue'] = properties_data.get('attributes').get('council-information').get('capital-value')
                
                house_item['buildingAge'] = properties_data.get('building-age')            
        yield house_item
