import pymysql
import os
from scrapy.utils.project import get_project_settings
from slugify import slugify
from scrapy import Request
from urllib import parse


def parse_detail():
    pass

def start_sync_homue_location():
    #example: https://platform.realestate.co.nz/search/v1/listings/42501188?include=agents,offices
    attributes_base_url = "https://platform.realestate.co.nz/search/v1/listings/"
    attributes_url_params = "agents,offices"
    realestate_header = {"Accept": "application/json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
        
    project_settings = get_project_settings()
    conn = pymysql.connect(
                host=project_settings['DB_HOST'], 
                user=project_settings['DB_USER'], 
                password=project_settings['DB_PASSWORD'], 
                database=project_settings['DB_DATABASE'], 
                port=project_settings['DB_PORT']
            )
    
    sql = f"SELECT id, region_id, slug FROM nz_city"
    cursor = conn.cursor()
    cursor.execute(sql)
    nz_city_results = cursor.fetchall()
    nz_cities = [{'region_id_slug': f"{item[1]}_{item[2]}", 'id': item[0]} for item in nz_city_results]

    sql = f"SELECT id, fq_slug FROM nz_district"
    cursor.execute(sql)
    nz_district_results = cursor.fetchall()
    nz_districts = [{'fq_slug': item[1], 'id': item[0]} for item in nz_district_results]
        
    sql = 'SELECT id, origin_house_id FROM homue_import_houses WHERE is_new_insert = 1 AND deleted_at IS NULL AND has_sold=0 AND has_verfied=0 AND districtId=0 AND districtName IS NOT NULL'
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        attributes_api_url = attributes_base_url + row[1] + '?include=' + parse.quote(attributes_url_params)
            
    cursor.close()
    conn.close()
    print('Sync location is Done!')
    
    
if __name__ == '__main__':
    start_sync_homue_location()          