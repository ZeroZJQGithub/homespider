import scrapy
import copy
from scrapy import Request
from scrapy.http import JsonRequest
from ..items import HomespiderItem
from urllib import parse
import json


class HomesSpiderSpider(scrapy.Spider):
    name = "homes_spider"
    allowed_domains = ["realestate.co.nz", "platform.realestate.co.nz"]
    realestate_header = {"Accept": "application/json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    house_category = 'business'
    start_urls = ["https://www.realestate.co.nz/business/sale?by=latest"]
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


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, headers=self.realestate_header, callback=self.parse)

    def parse(self, response):
        # pass
        if self.house_category == 'business':
            for house in response.css('div.listing-tile'):
                detail_page_link = house.css("div.tile--body>div.relative a::attr(href)").get()
                # self.log(detail_page_link)
                # detail_page_link = self.root_url + detail_page_link
                if detail_page_link is not None:
                    house_id = detail_page_link.split("/")[1]
                    attributes_api_url = self.attributes_base_url + house_id + '?include=' + parse.quote(self.attributes_url_params)
                    # self.log(f"url: {attributes_api_url}")
                    yield Request(attributes_api_url, headers=self.realestate_header, callback=self.parse_detail)
        else:
            for house in response.css('div.listing-tile'):
                detail_page_link = house.css('div.swiper-wrapper a::attr(href)').get()
                if detail_page_link is not None:
                    detail_page_link = self.root_url + detail_page_link
                    # self.log(detail_page_link)
                    house_id = detail_page_link.split("/")[3]
                    attributes_api_url = self.attributes_base_url + house_id + '?include=' + parse.quote(self.attributes_url_params)
                    self.log(attributes_api_url)

                    yield Request(attributes_api_url, headers=self.realestate_header, callback=self.parse_detail)
            
    def parse_detail(self, response):
        # pass
        json_data = json.loads(response.text)
        data = json_data.get('data')
        house_attributes = data.get('attributes')
        detail_address = house_attributes.get('address')
        included_data = json_data.get('included')
        house_item = HomespiderItem()
        house_item['url'] = house_attributes.get('website-full-url')
        house_item['houseId'] = data.get('id')
        house_item['listing_no'] = house_attributes.get('listing-no')
        house_item['category'] = self.house_category
        house_item['regionName'] = detail_address.get('region')
        house_item['cityName'] = detail_address.get('district')
        house_item['districtName'] = detail_address.get('suburb')
        house_item['streetName'] = detail_address.get('street')
        house_item['streetNumber'] = detail_address.get('street-number')
        house_item['unitNumber'] = detail_address.get('unit-number')
        house_item['propertyType'] = house_attributes.get('listing-sub-type')
        house_item['ownership'] = house_attributes.get('title-type')
        house_item['priceDisplay'] = house_attributes.get('price-display')
        house_item['priceCode'] = house_attributes.get('price-code')
        house_item['auctionTime'] = house_attributes.get('auction-time')
        house_item['auctionAddress'] = house_attributes.get('auction-location')
        house_item['tenderTime'] = house_attributes.get('tender-date')
        house_item['deadlineTime'] = house_attributes.get('deadline-date')
        house_item['openHomeTimes'] = house_attributes.get('open-homes')
        house_item['landArea'] = house_attributes.get('land-area')
        house_item['landAreaUnit'] = house_attributes.get('land-area-unit')
        house_item['floorArea'] = house_attributes.get('floor-area')
        house_item['floorAreaUnit'] = house_attributes.get('floor-area-unit')
        house_item['bedrooms'] = house_attributes.get('bedroom-count')
        house_item['bathrooms'] = house_attributes.get('bathroom-count')
        house_item['parkingMainRoof'] = house_attributes.get('parking-garage-count')
        house_item['parkingFreestanding'] = house_attributes.get('parking-other-count')   
        house_item['parkingSpaces'] = house_attributes.get('parking-covered-count')  
        # house_item['exteriorMaterial'] = house_attributes.get('parking-covered-count')
        # house_item['roofMaterial'] = house_attributes.get('parking-covered-count')
        house_item['otherFacilities'] = house_attributes.get('other-features')  
        house_item['title'] = detail_address.get('full-address')
        house_item['englishDescription'] = house_attributes.get('description')
        # house_item['floorPlanPhotos'] = house_attributes.get('floorplans')
        house_item['videoSrc'] = house_attributes.get('videos')
        house_item['latitude'] = detail_address.get('latitude')
        house_item['longtitude'] = detail_address.get('longitude')
        house_item['address'] = detail_address.get('full-address')
        house_item['subtitle'] = house_attributes.get('header')
        house_item['features'] = house_attributes.get('features')
        house_item['detail_address'] = detail_address
        # house_item['is_spided'] = 0

        # house_item['agency'] = included_data[0].get('attributes')
        # house_item['agent'] = included_data[1].get('attributes')
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
        if house_attributes.get('floorplans') != "":
            for photo_item in house_attributes.get('floorplans'):
                photo = {"original_name": "", "url": photo_item.get('url')}
                floorPlanPhotos.append(photo)
            house_item['floorPlanPhotos'] = floorPlanPhotos

        child_cares = house_attributes.get('child-cares')
        house_item['childCares'] = child_cares

        propertyShortId = house_attributes.get('property-short-id')
        house_item['propertyShortId'] = propertyShortId
        schools = house_attributes.get('schools')
        if schools is not None:
            schools_params = {
                'filter[geocode]': f"{detail_address.get('longitude')},{detail_address.get('latitude')}",
                'filter[includeNearby]': 'true',
                'page[responseType]': 'no-geo',
                'page[limit]': 50

            }
            schools_url = self.schools_base_url + parse.urlencode(schools_params)
            yield Request(schools_url, headers=self.realestate_header, callback=self.parse_schools, meta={'house_item': house_item})
        elif child_cares is not None:
            child_cares_params = ''
            for child_care in child_cares:
                child_cares_params += f"filter[ids][]={child_care.get('short-id')}&"

            child_cares_params += 'page[limit]=50'
            child_cares_params = child_cares_params.replace('[', '%5B').replace(']', '%5D')
            child_cares_url = self.childcares_base_url + child_cares_params
            yield Request(child_cares_url, headers=self.realestate_header, callback=self.parse_child_cares, meta={'house_item': house_item})
        elif propertyShortId is not None:
            property_url = self.properties_base_url + propertyShortId
            yield Request(property_url, headers=self.realestate_header, callback=self.parse_properties, meta={'house_item': house_item})
        else:
            yield house_item

    def parse_schools(self, response):
        house_item = response.meta['house_item']
        json_data = json.loads(response.text)
        schools_data = json_data['data']
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

        # yield house_item

        child_cares = house_item['childCares']
        propertyShortId = house_item['propertyShortId']
        if child_cares is not None:
            child_cares_params = ''
            for child_care in child_cares:
                child_cares_params += f"filter[ids][]={child_care.get('short-id')}&"

            child_cares_params += 'page[limit]=50'
            child_cares_params = child_cares_params.replace('[', '%5B').replace(']', '%5D')
            child_cares_url = self.childcares_base_url + child_cares_params
            yield Request(child_cares_url, headers=self.realestate_header, callback=self.parse_child_cares, meta={'house_item': house_item})

        elif propertyShortId is not None:
            property_url = self.properties_base_url + propertyShortId
            yield Request(property_url, headers=self.realestate_header, callback=self.parse_properties, meta={'house_item': house_item})

        else:
            yield house_item

    def parse_child_cares(self, response):
        house_item = response.meta['house_item']
        json_data = json.loads(response.text)
        child_cares_data = json_data['data']
        child_cares = house_item['childCares']
        new_child_cares = []
        if child_cares_data is not None:
            for child_care in child_cares_data:
                for pre_child_care in child_cares:
                    if child_care.get('id') == pre_child_care.get('short-id'):
                        new_child_care = {}
                        new_child_care.update(child_care.get('attributes'))
                        need_pre_child_care = {'geo-radius': pre_child_care.get('geo-radius'), 'in-zone': pre_child_care.get('in-zone'), 'has-zone': pre_child_care.get('has-zone')}
                        new_child_care.update(need_pre_child_care)
                        new_child_cares.append(new_child_care)

            house_item['childCares'] = new_child_cares

        # yield house_item

        propertyShortId = house_item['propertyShortId']
        if propertyShortId is not None:
            property_url = self.properties_base_url + propertyShortId
            yield Request(property_url, headers=self.realestate_header, callback=self.parse_properties, meta={'house_item': house_item})
        else:
            yield house_item

    
    def parse_properties(self, response):
        house_item = response.meta['house_item']
        json_data = json.loads(response.text)
        properties_data = json_data['data']

        council_information = properties_data.get('attributes').get('council-information')
        if council_information is not None:
            house_item['capitalValue'] = properties_data.get('attributes').get('council-information').get('capital-value')
        
        house_item['buildingAge'] = properties_data.get('building-age')

        yield house_item

    



        




        
        


        


        
        

