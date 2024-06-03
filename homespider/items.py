# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HomespiderItem(scrapy.Item):
    # define the fields for your item here like:
    houseId = scrapy.Field() #对应homue_import_houses的origin_house_id
    category = scrapy.Field()   #房屋类别
    propertyType = scrapy.Field() #物业属性
    ownership = scrapy.Field() #房屋所有权      (在pipelines中填充)
    currentStatus = scrapy.Field() #当前状态    (暂无对应项)
    expectedSalePrice = scrapy.Field() #期望售价(新增)(暂无对应项)
    capitalValue = scrapy.Field() #税务估值(v2版)
    capitalValueUnavailable = scrapy.Field() #是否有税务估值(新增)(在pipelines中填充)
    openHomeTimes = scrapy.Field()
    regionId = scrapy.Field()  #(在pipelines中填充)
    cityId = scrapy.Field()     #(在pipelines中填充)
    districtId = scrapy.Field() #(在pipelines中填充)
    unitNumber = scrapy.Field()
    streetNumber = scrapy.Field()
    streetName = scrapy.Field()
    title = scrapy.Field() #标题
    chineseTitle = scrapy.Field() #中文标题(新增)(暂无对应项)
    englishDescription = scrapy.Field() #英文描述
    chineseDescription = scrapy.Field() #中文描述(暂无对应项)

    landArea = scrapy.Field()       #土地面积
    floorArea = scrapy.Field()      #建筑面积
    rooms = scrapy.Field()          #(暂无对应项)
    bedrooms = scrapy.Field()       
    bathrooms = scrapy.Field()
    garageParking = scrapy.Field() #车库(v2版)需改名称parkingMainRoof
    offStreetParking = scrapy.Field() #停车位(v2版)需改名称parkingSpaces
    exteriorMaterial = scrapy.Field()   #外墙材料(暂无对应项)
    roofMaterial = scrapy.Field() #屋顶材料(暂无对应项)
    structureType = scrapy.Field() #建筑结构(新增)(暂无对应项)
    buildingAge = scrapy.Field() #建筑年代
    amenities = scrapy.Field() #便利设施（新增）
    views = scrapy.Field() #景观 暂缺
    developmentOpportunities = scrapy.Field() #开发机会 暂缺(V2去掉)
    primarySchool = scrapy.Field() #小学 (json)
    intermediateSchool = scrapy.Field() #中学(json)
    secondarySchool = scrapy.Field() #高中(json)


    salesMethod = scrapy.Field() #销售方式
    askingPrice = scrapy.Field() #要价（新增）
    # enquiryOver = scrapy.Field()    #问询价
    enquiriesOver = scrapy.Field() #问询价(V2)需改名称enquiryOver
    negotiableFrom = scrapy.Field() #议价起价(新增)
    auctionTime = scrapy.Field()    #拍卖时间
    tenderTime = scrapy.Field()     #招标时间
    tenderOffersOver = scrapy.Field() #招标起价(新增)
    deadlineTime = scrapy.Field()   #截止时间


    propertyInDeal = scrapy.Field() #资产类型(暂无对应项)
    leaseTerm = scrapy.Field() #租约期限(暂无对应项)
    rentPerYear = scrapy.Field() #年租金(暂无对应项)
    annualAverageIncome = scrapy.Field() #年平均收入需改名称yearlyAverageIncome(暂无对应项)
    annualProfitBeforeTax = scrapy.Field() #年平均收入需改名称yearlyProfitBeforeTax(暂无对应项)
    invoiceValueOfFixedAssets = scrapy.Field() #固定资产发票价值(暂无对应项)
    netValueOfFixedAssets = scrapy.Field() #固定资产净值(暂无对应项)
    yearsInBusiness = scrapy.Field() #营业年限(暂无对应项)
    passingOnStaff = scrapy.Field() #员工(暂无对应项)
    licensesAchieved = scrapy.Field() #已获得的许可证(暂无对应项)

    photos = scrapy.Field() #照片
    floorPlanPhotos = scrapy.Field() #户型图
    videoSrc = scrapy.Field() #视频
    virtualTourSrc = scrapy.Field() #3D虚拟
    latitude = scrapy.Field() #纬度
    longtitude = scrapy.Field() #经度
    keywords = scrapy.Field() #关键词
    address = scrapy.Field() #地址
    partnerIds = scrapy.Field() #合作伙伴ID(未插入数据库)

    #以下为后台额外所需字段
    url = scrapy.Field()        #房源地址
    listing_no = scrapy.Field()
    regionName = scrapy.Field()
    cityName = scrapy.Field()
    districtName = scrapy.Field()
    slugRegion = scrapy.Field()
    otherFacilities = scrapy.Field() #其它设施(json)(暂时无用)
    childCares = scrapy.Field() #不对应，可以去掉(json)(暂时无用)
    agent = scrapy.Field() #(json)
    agents = scrapy.Field() #(json)
    agency = scrapy.Field() #(json)
    auctionAddress = scrapy.Field() #不对应，可以去掉(暂时无用)
    detail_address = scrapy.Field() #不对应，可以去掉(json)
    subtitle = scrapy.Field()
    pubished_date = scrapy.Field()
    priceDisplay = scrapy.Field() #不对应，可以去掉
    priceCode = scrapy.Field() #不对应，可以去掉
    landAreaUnit = scrapy.Field() #不对应，可以去掉
    floorAreaUnit = scrapy.Field() #不对应，可以去掉
    propertyShortId = scrapy.Field() #不对应，可以去掉
    image_paths = scrapy.Field()
    hasSwimmingPool = scrapy.Field()
    listing_type = scrapy.Field()
    created_at = scrapy.Field()

    # features = scrapy.Field() #(json)(暂时无用)(删除)
    # description = scrapy.Field() #不对应，可以去掉(删除)
    # rateableValue = scrapy.Field()  #税务估值:已更改为capitalValue
    # indictativePrice = scrapy.Field()   #指导价（V2去掉)
    # parkingMainRoof = scrapy.Field()    #车库
    # parkingFreestanding = scrapy.Field()    #独立车库
    # parkingSpaces = scrapy.Field()      #停车位
    # survelianceSystem = scrapy.Field() #监控系统 暂缺(V2去掉)
    # accessControlSystem = scrapy.Field() #出入控制系统 暂缺(V2去掉)
    # ventilatingSystem = scrapy.Field() #通风系统 暂缺(V2去掉)
    # heatingSystem = scrapy.Field() #供暖系统 暂缺(V2去掉)
    # internetConnectivity = scrapy.Field() # 网络连接 暂缺(V2去掉)
    # agencyRef = scrapy.Field() #代理编号 暂缺(V2去掉)
    # endOfLease = scrapy.Field() #租约到期(V2去掉)
    # serviceBuildings = scrapy.Field() #服务建筑(V2去掉)
    # yearlyAverageIncome = scrapy.Field() #年平均收入
    # yearlyAverageCost = scrapy.Field() #年平均成本(V2去掉)
    # yearlyProfitBeforeTax = scrapy.Field() #年税前利润
    # is_spided = scrapy.Field()
    # pass
