from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import scrapy
import os
from datetime import datetime
import scrapy.utils
import scrapy.utils.project

root_url = "https://www.realestate.co.nz"
# nz_regions_size = 21
nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
house_categories = ['residential', 'commercial', 'rural', 'business']

region_index = -1
category_index = -1



def start_spider():
    global region_index, category_index, nz_regions, house_categories, root_url
    scrapy.utils.project.inside_project = lambda: True
    region_index = (region_index + 1) % 21
    if region_index == 0:
        category_index  = category_index + 1
    if category_index < 4:
        url = f'{root_url}/{house_categories[category_index]}/sale/{nz_regions[region_index]}?by=latest'
        print(f'The current spider url is: {url}')
        os.system(f'scrapy crawl home_defferred -a url={url}')
    else:
        pass

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    trigger = IntervalTrigger(hours=5, start_date=datetime.now())
    job = scheduler.add_job(start_spider, trigger)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.remove_job(job.id)    