"""
需要pip3 install redis
"""

from redis import StrictRedis
from urllib.parse import quote


# def set_task():
#     sr = StrictRedis(host='39.105.214.53', port=6379, db=0)
#     #起始urls，根据分类添加url地址
#     start_urls = [
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=degree&pageSize=50&page=1&searchWord=%E6%B3%95%E5%BE%8B&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=degree',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=degree&pageSize=50&page=1&searchWord=%E6%94%BF%E6%B2%BB&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=degree',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=perio&pageSize=50&page=1&searchWord=%E6%94%BF%E6%B2%BB&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=perio',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=perio&pageSize=50&page=1&searchWord=%E6%B3%95%E5%BE%8B&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=perio',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=conference&pageSize=50&page=1&searchWord=%E6%B3%95%E5%BE%8B&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=conference',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=conference&pageSize=50&page=1&searchWord=%E6%94%BF%E6%B2%BB&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=conference',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=tech&pageSize=50&page=1&searchWord=%E6%B3%95%E5%BE%8B&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=tech',
#         'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=tech&pageSize=50&page=1&searchWord=%E6%94%BF%E6%B2%BB&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=tech',
#     ]
#
#     #分类，根据分类和年限时间段添加url地址
#     category = ['degree','conference','perio','tech']
#     #年份(1990,2019)
#     dataList = []
#     for i in range(1990,2020):
#         dataList.append(i)
#
#     index = 0
#     # 关键字
#     searchWords = ['法律','政治']
#     # (政治) 起始年:2010 结束年:2019
#     search_words = []
#     for i in dataList:
#         index += 1
#         for j in dataList[index:]:
#             for word in searchWords:
#                 search_words.append('(%s) 起始年:%s 结束年:%s' % (word,i,j))
#
#     for cate in category:
#         for keyWord in reversed(search_words):
#             full_url = 'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=%s&pageSize=50&page=1&searchWord=%s&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=%s' % (cate,quote(keyWord),cate)
#             print(full_url)
#             start_urls.append(full_url)
#
#
#     #将目标url添加到redis数据库，注意wflunwen:start_urls，一定不要写错了
#     for url in start_urls:
#         print(url)
#         sr.lpush('wflunwen:start_urls',url)

# 添加起始任务
def set_wanfangtask():
    sr = StrictRedis(host='39.105.214.53', port=6379, db=0)
    # 起始urls格式参考
    # start_urls = [
    #     # 政治
    #     'http://s.wanfangdata.com.cn/Paper.aspx?q=%e6%94%bf%e6%b2%bb+DBID%3aWF_QK&f=top&p=1',
    #     'http://s.wanfangdata.com.cn/Paper.aspx?q=%e6%94%bf%e6%b2%bb+DBID%3aWF_XW&f=top&p=1',
    #     'http://s.wanfangdata.com.cn/Paper.aspx?q=%e6%94%bf%e6%b2%bb+DBID%3aWF_HY&f=top&p=1',
    #     # 法律
    #     'http://s.wanfangdata.com.cn/Paper.aspx?q=%e6%b3%95%e5%be%8b+DBID%3aWF_QK&f=top&p=1',
    #     'http://s.wanfangdata.com.cn/Paper.aspx?q=%e6%b3%95%e5%be%8b+DBID%3aWF_XW&f=top&p=1',
    #     'http://s.wanfangdata.com.cn/Paper.aspx?q=%e6%b3%95%e5%be%8b+DBID%3aWF_HY&f=top&p=1',
    # ]
    #设置起始url的地址
    start_urls = []
    # 分类，根据分类和年限时间段添加url地址
    # QK：期刊 XW：学位 HY：会议
    categorys = ['QK','XW','HY']
    # 关键字
    searchWords = ['法律','政治']
    for page in range(1, 2):
        # page 表示页码（例如：range(10, 100)：表示设置各分类的起始任务为10～100页，这里只需要给出一部分分页地址，在具体的代码中，会自动获取其他分页）
        # 注意：因为之前爬虫运行过了，redis数据库中保存着去重的指纹信息，设置的起始url可能之前爬取过了，所以起始url和截止url间区范围可以适当大一些
        for category in categorys:
            for searchWord in searchWords:
                #由这几个部分组成完整的url地址
                url = 'http://s.wanfangdata.com.cn/Paper.aspx?q=%s+DBID%sWF_%s&f=top&p=%s' % (quote(searchWord),'%3a',category,str(page))
                print(url)
                start_urls.append(url)
    #添加科技报告url地址
    #http://s.wanfangdata.com.cn/NSTR.aspx?q=%E6%94%BF%E6%B2%BB&f=top
    #http://s.wanfangdata.com.cn/NSTR.aspx?q=%e6%94%bf%e6%b2%bb&f=top&p=2
    for page in range(1,2):
        for searchWord in searchWords:
            url = 'http://s.wanfangdata.com.cn/NSTR.aspx?q=%s&f=top&p=%s' % (quote(searchWord),page)
            print(url)
            start_urls.append(url)
    return start_urls
    # 将目标url添加到redis数据库，注意wflunwen:start_urls，一定不要写错了
    # for url in start_urls:
    #     print(url)
    #     sr.lpush('wflunwen:start_urls', url)

if __name__ == '__main__':

    #set_task()
    set_wanfangtask()

