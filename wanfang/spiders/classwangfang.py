# -*- coding: utf-8 -*-
import scrapy,re
from classtask import get_start_urls,get_old_start_urls
from urllib.parse import quote,unquote
from wanfang.items import WanfangDegreeItem,WanfangPerioItem,WanfangConferenceItem,WanfangTechItem
from scrapy_redis.spiders import RedisSpider

#class ClasswangfangSpider(scrapy.Spider):
class ClasswangfangSpider(RedisSpider):
    name = 'classwangfang'
    allowed_domains = ['wanfangdata.com.cn']
   # start_urls = get_old_start_urls()
    redis_key = 'classwangfang:start_urls'

    def parse(self, response):
        """
        1。解析每一个分类下列表数据，根据每一个旧版的论文详情url地址，
        构建新版的论文详情URL地址，
        2。提取当前分页下其他分页的url地址，继续发起请求
        :param response:
        :return:
        """
        if 'Paper' in response.url:
            #http://s.wanfangdata.com.cn/Paper.aspx?q=jsbckasbc+DBID%sWF_%s&f=top&p=1
            pattern = re.compile('.*?q=(.*?)\+DBID')
            searchWord = unquote(re.findall(pattern,response.url)[0])
        else:
            #http://s.wanfangdata.com.cn/%s.aspx?q=%s&f=top&p=1
            pattern = re.compile('.*?q=(.*?)&f')
            searchWord = unquote(re.findall(pattern, response.url)[0])

        itemDivs = response.xpath('//div[@class="record-item-list"]/div')
        for item in itemDivs:
            #标题
            title = item.xpath('.//a[@class="title"]/text()').extract_first('')
            #获取详情的url地址
            itemUrl = item.xpath('.//a[@class="title"]/@href').extract_first('')
            #http://d.old.wanfangdata.com.cn/Claw/D620052276
            #http://d.old.wanfangdata.com.cn/Periodical/tfxl201603011
            itemId = itemUrl.split('/')[-2:][1]
            if itemId == '':
                itemId = itemUrl.split('/')[-2:][0]
            print(itemId)
            tags = ['QK','XW','HY']
            paths = ['patent','NSTR','Claw']
            if 'QK' in response.url:
                #期刊
                #http://www.wanfangdata.com.cn/details/detail.do?
                # _type=perio&id=gxzs-ll201006043
                fullUrl = 'http://www.wanfangdata.com.cn/details/detail.do?_type=perio&id='+itemId
                info = {'searchKey':searchWord,'searchType':'perio'}
            elif 'XW' in response.url:
                #学位
                #http://www.wanfangdata.com.cn/details/detail.do?
                # _type=degree&id=D01551993
                fullUrl = 'http://www.wanfangdata.com.cn/details/detail.do?_type=degree&id='+itemId
                info = {'searchKey': searchWord, 'searchType': 'degree'}
            elif 'HY' in response.url:
                #会议
                #http://www.wanfangdata.com.cn/details/detail.do?
                # _type=conference&id=9372841
                fullUrl = 'http://www.wanfangdata.com.cn/details/detail.do?_type=conference&id='+itemId
                info = {'searchKey': searchWord, 'searchType': 'conference'}
            elif 'patent' in response.url:
                # 专利
                #http://www.wanfangdata.com.cn/details/detail.do?
                # _type=patent&id=CN201830201432.8
                fullUrl = 'http://www.wanfangdata.com.cn/details/detail.do?_type=patent&id='+itemId
                info = {'searchKey': searchWord, 'searchType': 'patent'}
            elif 'NSTR' in response.url:
                #科技报告
                #http://www.wanfangdata.com.cn/details/detail.do?
                # _type=tech&id=66753
                fullUrl = 'http://www.wanfangdata.com.cn/details/detail.do?_type=tech&id='+itemId
                info = {'searchKey': searchWord, 'searchType': 'tech'}
            elif 'Claw' in response.url:
                #法规
                #http://www.wanfangdata.com.cn/details/detail.do?
                # _type=legislations&id=G000283738
                fullUrl = 'http://www.wanfangdata.com.cn/details/detail.do?_type=legislations&id='+itemId
                info = {'searchKey': searchWord, 'searchType': 'legislations'}

            #发起详情的请求
            yield scrapy.Request(fullUrl,callback=self.parsePaperDetail,meta=info)

        print(response.status,response.url)

        #提取其他分页继续发起请求
        other_pages = response.xpath('//p[@class="pager"]/a/@href').extract()
        if len(other_pages):
            for url in other_pages:
                pageUrl = response.urljoin(url)
                yield scrapy.Request(pageUrl,callback=self.parse)

    def parsePaperDetail(self,response):
        searchType = response.meta['searchType']
        if searchType == 'perio':
            #解析期刊的详情内容
            item = self.get_perio_detail(response,response.meta)
        elif searchType == 'degree':
            # 解析学位的详情内容
            item = self.get_degree_detail(response,response.meta)
        elif searchType == 'conference':
            # 解析会议的详情内容
            item = self.get_conference_detail(response, response.meta)
        elif searchType == 'patent':
            # 解析专利的详情内容
            item = self.get_patent_detail(response, response.meta)
        elif searchType == 'tech':
            # 解析科技报告的详情内容
            item = self.get_tech_detail(response, response.meta)
        elif searchType == 'legislations':
            # 解析法规的详情内容
            item = self.get_legislations_detail(response, response.meta)
        yield item

    def get_perio_detail(self,response,info):
        item = WanfangPerioItem()
        item['url'] = response.url
        # title(中文标题)
        item['title'] = response.xpath('//div[@class="title"]/text()').extract_first('').replace('\r\n', '').replace(
            ' ', '').replace('\t', '')
        # englishTitle(英文标题)
        item['englishTitle'] = response.xpath('//div[@class="English"]/text()').extract_first('暂无').replace('\t', '')
        # content(摘要)
        # item['content'] = ''.join(response.xpath('//input[@class="share_summary"]/@value').extract()).replace('\t',
        #                                                                                                      '').replace(
        #     ' ', '').replace('\r\n', '')
        item['content'] = ''.join(response.xpath('//div[@class="abstract"]/textarea/text()').extract()).replace(
            '\u3000', '').replace('\t', '').replace(' ', '').replace('\n', '')

        lis = response.xpath('//ul[@class="info"]//li')
        print(len(lis))
        for li in lis:
            # print(li.xpath('./div[@class="info_left"]/text()').extract_first(''))
            if li.xpath('./div[@class="info_left"]/text()').extract_first('') == "doi：":
                item['doi'] = li.xpath('.//a/text()').extract_first('').replace('\t', '').replace(' ', '')
            elif li.xpath('./div[@class="info_left "]/text()').extract_first('') == "关键词：":
                # keywords(关键词)
                item['keywords'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "Keyword：":
                item['englishKeyWords'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者：":
                item['authors'] = '、'.join(
                    li.xpath('./div[@class="info_right"]/a[@class="info_right_name"]/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "Author：":
                item['englishAuthors'] = '、'.join(
                    li.xpath('./div[@class="info_right"]/a[@class="info_right_name"]/text()').extract()).replace('\n',
                                                                                                                 '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者单位：":
                item['unit'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "刊名：":
                item['journalName'] = li.xpath('.//a[@class="college"]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "Journal：":
                item['journal'] = li.xpath('.//a[1]/text()').extract_first('')
                if len(item['journal']) == 0:
                    item['journal'] = li.xpath('.//div[2]/text()').extract_first('').replace('\r\n', '').replace(' ',
                                                                                                                 '').replace(
                        '\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "年，卷(期)：":
                item['yearsInfo'] = li.xpath('.//a/text()').extract_first('')
                if len(item['yearsInfo']) == 0:
                    item['yearsInfo'] = li.xpath('.//div[2]/text()').extract_first('').replace('\r\n', '').replace(' ',
                                                                                                                   '').replace(
                        '\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "所属期刊栏目：":
                item['journalSection'] = li.xpath('.//a/text()').extract_first('')
                if len(item['journalSection']) == 0:
                    item['journalSection'] = li.xpath('.//div[2]/text()').extract_first('').replace('\r\n', '').replace(
                        ' ',
                        '').replace(
                        '\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "分类号：":
                item['classNumber'] = li.xpath('.//div[2]/text()').extract_first('').replace('\r', '').replace('\n',
                                                                                                               '').replace(
                    '\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "基金项目：":
                item['fundProgram'] = li.xpath('.//a[1]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "在线出版日期：":
                item['publishTime'] = li.xpath('.//div[2]/text()').extract_first('').replace('\r\n', '').replace(' ',
                                                                                                                 '').replace(
                    '\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "页数：":
                item['pages'] = li.xpath('.//div[2]/text()').extract_first('').replace(' ', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "页码：":
                item['pageNumber'] = li.xpath('.//div[2]/text()').extract_first('').replace(' ', '')

        item['searchKey'] = info['searchKey']
        item['searchType'] = info['searchType']

        return item

    def get_degree_detail(self,response,info):
        item = WanfangDegreeItem

        item['url'] = response.url
        # title(中文标题)
        item['title'] = ''.join(response.xpath('//div[@class="title"]/text()').extract()).replace('\r\n', '').replace(
            '\t', '').replace('目录', '').replace(' ', '')

        # content(摘要)
        # item['content'] = ''.join(response.xpath('//input[@class="share_summary"]/@value').extract()).replace('\t',
        #                                                                                                       '').replace(
        #     ' ', '').replace('\r\n', '')
        item['content'] = ''.join(response.xpath('//div[@class="abstract"]/textarea/text()').extract()).replace(
            '\u3000', '').replace('\t', '').replace(' ', '').replace('\n', '')

        lis = response.xpath('//ul[@class="info"]//li')
        print(len(lis))
        for li in lis:
            if li.xpath('./div[@class="info_left"]/text()').extract_first('') == "关键词：":
                # keywords(关键词)
                item['keywords'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者：":
                # authors(作者)
                item['authors'] = li.xpath('.//a[1]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "学位授予单位：":
                # 学位授权单位
                item['degreeUnit'] = li.xpath('.//a[1]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "授予学位：":
                # 授予学位
                item['awardedTheDegree'] = li.xpath('./div[@class="info_right author"]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "学科专业：":
                # 学科专业
                item['professional'] = li.xpath('.//a[1]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "导师姓名：":
                # 导师姓名
                item['mentorName'] = li.xpath('.//a[1]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "学位年度：":
                # 学位年度
                item['degreeInAnnual'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "语种：":
                # 语种
                item['languages'] = li.xpath('./div[2]/text()').extract_first('').replace('\r\n', '').replace('\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "分类号：":
                # 分类号
                item['classNumber'] = ' '.join(li.xpath('./div[2]//text()').extract()).replace('\r\n', ' ').replace(
                    '\t', '').strip(' ')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "在线出版日期：":
                # 在线出版日期
                item['publishTime'] = li.xpath('./div[2]/text()').extract_first('').replace('\r\n', '').replace('\t',
                                                                                                                '').replace(
                    ' ', '')
        item['searchKey'] = info['searchKey']
        item['searchType'] = info['searchType']

        return item

    def get_conference_detail(self,response,info):

        item = WanfangConferenceItem()
        item['url'] = response.url
        # title(中文标题)
        item['title'] = ''.join(response.xpath('//div[@class="title"]/text()').extract()).replace('\r\n', '').replace(
            '\t', '').replace('目录', '').replace(' ', '')
        # content(摘要)
        # item['content'] = ''.join(response.xpath('//input[@class="share_summary"]/@value').extract()).replace('\t','').replace(' ', '').replace('\r\n', '').replace('\u3000', '')
        item['content'] = ''.join(response.xpath('//div[@class="abstract"]/textarea/text()').extract()).replace(
            '\u3000', '').replace('\t', '').replace(' ', '').replace('\n', '')

        lis = response.xpath('//ul[@class="info"]//li')
        print(len(lis))
        for li in lis:
            if li.xpath('./div[@class="info_left"]/text()').extract_first('') == "关键词：":
                # keywords(关键词)
                item['keywords'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者：":
                # authors(作者)
                item['authors'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者单位：":
                # 作者单位
                item['unit'] = '、'.join(li.xpath('.//a[1]/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "母体文献：":
                # 母体文献
                item['literature'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "会议名称：":
                # 会议名称
                item['meetingName'] = li.xpath('./div[2]/a[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "会议时间：":
                # 会议时间
                item['meetingTime'] = li.xpath('./div[2]/text()').extract_first('').replace('\r\n', '').replace('\t',
                                                                                                                '').replace(
                    ' ', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "会议地点：":
                # 会议地点
                item['meetingAdress'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "主办单位：":
                # 主办单位
                item['organizer'] = '、'.join(li.xpath('./div[2]//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "语 种：":
                # 语种
                item['languages'] = li.xpath('./div[2]/text()').extract_first('').replace('\r\n', '').replace('\t', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "分类号：":
                # 分类号
                item['classNumber'] = ''.join(li.xpath('./div[2]/text()').extract()).replace('\r\n', '').replace('\t',
                                                                                                                 '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "在线出版日期：":
                # 发布时间
                item['publishTime'] = li.xpath('./div[2]/text()').extract_first('').replace('\r\n', '').replace('\t',
                                                                                                                '').replace(
                    ' ', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "页码：":
                # 页码
                item['pageNumber'] = li.xpath('./div[2]/text()').extract_first('')
        item['searchKey'] = info['searchKey']
        item['searchType'] = info['searchType']
        return item

    def get_patent_detail(self,response,info):
        pass

    def get_tech_detail(self,response,info):
        item = WanfangTechItem()
        item['url'] = response.url
        # title(中文标题)
        item['title'] = response.xpath('//div[@class="title"]/text()').extract_first('').replace('\r\n', '').replace(
            ' ', '').replace('\t', '')
        # englishTitle(英文标题)
        item['englishTitle'] = response.xpath('//div[@class="English"]/text()').extract_first('暂无').replace('\t', '')
        # content(摘要)
        # item['content'] = ''.join(response.xpath('//input[@class="share_summary"]/@value').extract()).replace('\t',
        #                                                                                                       '').replace(
        #     ' ', '').replace('\r\n', '')
        item['content'] = ''.join(response.xpath('//div[@class="abstract"]/textarea/text()').extract()).replace('\u3000','').replace('\t','').replace(' ', '').replace('\n','')

        lis = response.xpath('//ul[@class="info"]//li')
        print(len(lis))
        for li in lis:
            if li.xpath('./div[@class="info_left"]/text()').extract_first('') == "关键词：":
                # keywords(关键词)
                item['keywords'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者：":
                # authors(作者)
                item['authors'] = '、'.join(li.xpath('.//a/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "作者单位：":
                # 作者单位
                item['unit'] = '、'.join(li.xpath('.//a[1]/text()').extract())
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "报告类型：":
                # 报告类型
                item['reportType'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "公开范围：":
                # 公开范围
                item['openRange'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "全文页数：":
                # 全文页数
                item['pageNumber'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "项目/课题名称：":
                # 项目/课题名称
                item['projectName'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "计划名称：":
                # 计划名称
                item['planName'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "编制时间：":
                # 编制时间
                item['compileTime'] = li.xpath('./div[2]/text()').extract_first('').replace('\t', '').replace(' ',
                                                                                                              '').replace(
                    '\r\n', '')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "立项批准年：":
                # 立项批准年
                item['approvalYear'] = li.xpath('./div[2]/text()').extract_first('')
            elif li.xpath('./div[@class="info_left"]/text()').extract_first('') == "馆藏号：":
                # 馆藏号
                item['collection'] = li.xpath('./div[2]/text()').extract_first('')

        item['searchKey'] = info['searchKey']
        item['searchType'] = info['searchType']

        return item

    def get_legislations_detail(self,response,info):
        pass



