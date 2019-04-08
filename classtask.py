#新版分析
# 分别获取
# 期刊、（政治和法律相关)
#政治相关第一页
# http://www.wanfangdata.com.cn/search/searchList.do?
# searchType=perio&showType=&pageSize=
# &searchWord=%E6%94%BF%E6%B2%BB&isTriggerTag=

#政治相关第二页
# http://www.wanfangdata.com.cn/search/searchList.do?
# beetlansyId=aysnsearch&searchType=perio&pageSize=20
# &page=2&searchWord=%E6%94%BF%E6%B2%BB&
# order=correlation&showType=detail&isCheck=check
# &isHit=&isHitUnit=&firstAuthor=false
# &rangeParame=&navSearchType=perio

#政治相关第三页
# http://www.wanfangdata.com.cn/search/searchList.do?
# beetlansyId=aysnsearch&searchType=perio&pageSize=20
# &page=3&searchWord=%E6%94%BF%E6%B2%BB&
# order=correlation&showType=detail&isCheck=check
# &isHit=&isHitUnit=&firstAuthor=false
# &rangeParame=&navSearchType=perio

#法律相关的第二页
#http://www.wanfangdata.com.cn/search/searchList.do?
# beetlansyId=aysnsearch&searchType=perio&pageSize=20
# &page=2&searchWord=%E6%B3%95%E5%BE%8B&
# order=correlation&showType=detail&isCheck=check
# &isHit=&isHitUnit=&firstAuthor=false
# &rangeParame=&navSearchType=perio

# 学位、
# 法律相关第二页
#http://www.wanfangdata.com.cn/search/searchList.do?
# beetlansyId=aysnsearch&searchType=degree&pageSize=20
# &page=2&searchWord=%E6%B3%95%E5%BE%8B&
# order=correlation&showType=detail&isCheck=check
# &isHit=&isHitUnit=&firstAuthor=false
# &rangeParame=&navSearchType=degree

#通过这两个url地址分析，
# 1.相通的搜索关键字下，分页的url地址只是searchType不同
# 2.在同一个分类下，搜索不同的关键字只是searchWord不同
# 会议、
#http://www.wanfangdata.com.cn/search/searchList.do?
# beetlansyId=aysnsearch&searchType=conference&pageSize=20
# &page=2&searchWord=%E6%B3%95%E5%BE%8B
# &order=correlation&showType=detail
# &isCheck=check&isHit=&isHitUnit=&firstAuthor=false
# &rangeParame=&navSearchType=conference
# 专利、(patent)
# 科技报告、
# 法规、
from urllib.parse import quote

def get_start_urls():
    # 通过规律构造每一个分类的，不同搜索关键字的起始页
    searchWords = ['法律','政治']
    categorys = ['perio','degree','conference','patent','tech','legislations']

    start_urls = []
    for category in categorys:
        for searchWord in searchWords:
            url = 'http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch&searchType=%s&pageSize=50&page=1&searchWord=%s&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=&navSearchType=%s' % (category,quote(searchWord),category)
            start_urls.append(url)

    print(len(start_urls))

    return start_urls

# 分析发现新版网站返回的条数有限制，
# 并且获取各个分类下的二级分类很多，
# 组合复杂

#==============================================

#分析旧版的url地址

#分别获取
# 期刊（QK,%e6%94%bf%e6%b2%bb）、（政治相关）
# 第二页
#http://s.wanfangdata.com.cn/Paper.aspx?
# q=%e6%94%bf%e6%b2%bb+DBID%3aWF_QK&f=top&p=2
#http://s.wanfangdata.com.cn/Paper.aspx?
# q=%e6%94%bf%e6%b2%bb+DBID%3aWF_QK&f=top&p=3
# 学位(XW)、（政治、法律）
#http://s.wanfangdata.com.cn/Paper.aspx?
# q=%e6%94%bf%e6%b2%bb+DBID%3aWF_XW&f=top&p=2
#http://s.wanfangdata.com.cn/Paper.aspx?
# q=%e6%94%bf%e6%b2%bb+DBID%3aWF_XW&f=top&p=3
# 会议(HY)、（政治、法律）
#http://s.wanfangdata.com.cn/Paper.aspx?
# q=%e6%94%bf%e6%b2%bb+DBID%3aWF_HY&f=top&p=2

# 专利、（政治、法律）
#http://s.wanfangdata.com.cn/patent.aspx?
# q=%e6%94%bf%e6%b2%bb&f=top&p=2
# 科技报告、（政治、法律）
#http://s.wanfangdata.com.cn/NSTR.aspx?
# q=%e6%94%bf%e6%b2%bb&f=top&p=2
# 法规
#http://s.wanfangdata.com.cn/Claw.aspx?
# q=%e6%94%bf%e6%b2%bb&f=top&p=3

import redis
def get_old_start_urls():
    #创建redis数据库链接
    redisClient = redis.StrictRedis(
        host='118.24.255.219',
        port=6380
    )
    # 通过规律构造每一个分类的，不同搜索关键字的起始页
    searchWords = ['法律', '政治']
    tags = ['QK','XW','HY']
    start_urls = []
    for tag in tags:
        for searchWord in searchWords:
            url = 'http://s.wanfangdata.com.cn/Paper.aspx?q=%s+DBID%sWF_%s&f=top&p=1' % (quote(searchWord),'%3a',tag)
            start_urls.append(url)

    paths = ['patent','NSTR','Claw']
    for path in paths:
        for searchWord in searchWords:
            url = 'http://s.wanfangdata.com.cn/%s.aspx?q=%s&f=top&p=1' % (path,quote(searchWord))
            start_urls.append(url)

    for url in start_urls:
        redisClient.lpush('classwangfang:start_urls',url)


if __name__ == '__main__':

    get_old_start_urls()


    #return start_urls

#http://s.wanfangdata.com.cn/Paper.aspx?
# q=%e6%b3%95%e5%be%8b+DBID%3aWF_QK&f=top&p=2

#旧版论文详情地址
#http://d.old.wanfangdata.com.cn/Periodical/
# gxzs-ll201006043
#新版的论文详情url地址
#http://www.wanfangdata.com.cn/details/detail.do?
# _type=perio&id=gxzs-ll201006043



