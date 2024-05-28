import pymysql
import os
from scrapy.utils.project import get_project_settings
# import logging
import json

def start_sync_local_images():
    project_settings = get_project_settings()
    conn = pymysql.connect(
                host=project_settings['DB_HOST'], 
                user=project_settings['DB_USER'], 
                password=project_settings['DB_PASSWORD'], 
                database=project_settings['DB_DATABASE'], 
                port=project_settings['DB_PORT']
            )
    sql = 'SELECT id, photos FROM homue_import_houses WHERE is_new_insert = 1 AND photos IS NOT NULL'
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    image_path = project_settings['IMAGES_STORE']
    for row in results:
        data_id = row[0]
        photos = json.loads(row[1])
        local_exists_images = []
        if len(photos) > 0:
            for photo in photos:
                photo_url = photo.get('url')
                image_name = photo_url.split('/')[-1]
                if os.path.exists(f'{image_path}/{image_name}') :
                    local_exists_images.append(image_name)
        if len(local_exists_images) > 0:
            local_exists_images = json.dumps(local_exists_images)
            sql = "UPDATE homue_import_houses SET image_paths=%s WHERE id=%s"
            cursor.execute(sql, (local_exists_images, data_id))
            conn.commit()       
    cursor.close()
    conn.close()
    print('Sync Local Images is Done!')

if __name__ == '__main__':
    start_sync_local_images()    
