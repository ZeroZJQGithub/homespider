# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HomespiderItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()        #房源地址
    category = scrapy.Field()   #房屋类别
    regionId = scrapy.Field()   
    regionName = scrapy.Field()
    cityId = scrapy.Field()
    cityName = scrapy.Field()
    districtId = scrapy.Field()
    districtName = scrapy.Field()
    unitNumber = scrapy.Field()
    streetNumber = scrapy.Field()
    streetName = scrapy.Field()
    propertyType = scrapy.Field()
    ownership = scrapy.Field()
    salesMethod = scrapy.Field()
    enquiryOver = scrapy.Field()    #问询价
    auctionTime = scrapy.Field()    #拍卖时间
    auctionAddress = scrapy.Field() #不对应，可以去掉
    tenderTime = scrapy.Field()     #招标时间
    deadlineTime = scrapy.Field()   #截止时间
    rateableValue = scrapy.Field()  #税务估值
    indictativePrice = scrapy.Field()   #指导价
    openHomeTimes = scrapy.Field()
    landArea = scrapy.Field()       #土地面积
    floorArea = scrapy.Field()      #建筑面积
    bedrooms = scrapy.Field()       
    bathrooms = scrapy.Field()
    rooms = scrapy.Field()
    parkingMainRoof = scrapy.Field()    #车库
    parkingFreestanding = scrapy.Field()    #独立车库
    parkingSpaces = scrapy.Field()      #停车位
    exteriorMaterial = scrapy.Field()   #外墙材料
    roofMaterial = scrapy.Field() #屋顶材料 暂缺
    buildingAge = scrapy.Field() #建筑年代 暂缺
    survelianceSystem = scrapy.Field() #监控系统 暂缺
    accessControlSystem = scrapy.Field() #出入控制系统 暂缺
    ventilatingSystem = scrapy.Field() #通风系统 暂缺
    heatingSystem = scrapy.Field() #供暖系统 暂缺
    internetConnectivity = scrapy.Field() # 网络连接 暂缺
    otherFacilities = scrapy.Field() #其它设施(json)
    views = scrapy.Field() #景观 暂缺
    developmentOpportunities = scrapy.Field() #开发机会 暂缺
    agencyRef = scrapy.Field() #代理编号 暂缺
    title = scrapy.Field() #标题
    englishDescription = scrapy.Field() #英文描述
    chineseDescription = scrapy.Field() #中文描述
    primarySchool = scrapy.Field() #小学 (json)
    intermediateSchool = scrapy.Field() #中学(json)
    secondarySchool = scrapy.Field() #高中(json)
    currentStatus = scrapy.Field() #当前状态
    endOfLease = scrapy.Field() #租约到期
    serviceBuildings = scrapy.Field() #服务建筑
    propertyInDeal = scrapy.Field() #资产类型
    leaseTerm = scrapy.Field() #租约期限
    rentPerYear = scrapy.Field() #年租金
    yearlyAverageIncome = scrapy.Field() #年平均收入
    yearlyAverageCost = scrapy.Field() #年平均成本
    yearlyProfitBeforeTax = scrapy.Field() #年税前利润
    yearsInBusiness = scrapy.Field() #营业年限
    invoiceValueOfFixedAssets = scrapy.Field() #固定资产发票价值
    netValueOfFixedAssets = scrapy.Field() #固定资产净值
    passingOnStaff = scrapy.Field() #员工
    licensesAchieved = scrapy.Field() #已获得的许可证
    photos = scrapy.Field() #照片
    floorPlanPhotos = scrapy.Field() #户型图
    videoSrc = scrapy.Field() #视频
    virtualTourSrc = scrapy.Field() #3D虚拟
    latitude = scrapy.Field() #纬度
    longtitude = scrapy.Field() #经度
    keywords = scrapy.Field() #关键词
    address = scrapy.Field() #地址
    partnerIds = scrapy.Field() #合作伙伴ID
    subtitle = scrapy.Field()
    # images = scrapy.Field()
    features = scrapy.Field() #(json)
    agents = scrapy.Field() #(json)
    
    capitalValue = scrapy.Field() #不对应，可以去掉
    priceDisplay = scrapy.Field() #不对应，可以去掉
    priceCode = scrapy.Field() #不对应，可以去掉
    landAreaUnit = scrapy.Field() #不对应，可以去掉
    floorAreaUnit = scrapy.Field() #不对应，可以去掉
    detail_address = scrapy.Field() #不对应，可以去掉(json)
    description = scrapy.Field() #不对应，可以去掉
    childCares = scrapy.Field() #不对应，可以去掉(json)
    propertyShortId = scrapy.Field() #不对应，可以去掉
    listing_no = scrapy.Field()
    houseId = scrapy.Field()
    agency = scrapy.Field()
    agent = scrapy.Field()
    pubished_date = scrapy.Field()
    image_paths = scrapy.Field()
    # is_spided = scrapy.Field()
    # pass
