import scrapy
from scrapy import Request
import requests.utils
import pymysql

class AgentLogoSpiderSpider(scrapy.Spider):
    name = "agent_logo_spider"
    allowed_domains = ["realestate.co.nz"]
    realestate_header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    start_url = "https://www.realestate.co.nz/search/results/agencies/"
    agencies = ["Harcourts", "Ray White", "LJ Hookers", "Bayleys", "Harveys", "Mike Pero", "Remax", "First National"]

    def start_requests(self):
        conn = pymysql.connect(
            host='192.168.150.128',
            user='root',
            password='123456',
            database='homue_api',
            port=3366
        )
        self.log(conn)
        cursor = conn.cursor()
        sql = "SELECT * FROM house_agency"
        cursor.execute(sql)
        results = cursor.fetchall()
        db_agencies = []
        for row in results:
            db_agency = {}
            db_agency['id'] = row[0]
            db_agency['name'] = row[1]
            db_agencies.append(db_agency)

        self.log(db_agencies)
        conn.close()
        for agency in db_agencies:
            self.log(f"{agency['id']}: {agency['name']}")
            yield Request(url= self.start_url + requests.utils.quote(agency['name']), headers=self.realestate_header, callback=self.parse, meta={'agency': agency})

    def parse(self, response):
        agency = response.meta['agency']
        agent_logo_url_item = response.xpath("//div/div[@data-test='office__card__search'][last()]")
        self.log(agent_logo_url_item)
        urls = agent_logo_url_item.xpath("a/div[1]/div/img/@src").getall()

        yield {
            'agency': agency,
            'agency_logo': urls
        }
