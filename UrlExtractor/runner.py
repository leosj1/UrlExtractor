import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# try:
#     execute(
#         [
#             'scrapy',
#             'crawl',
#             'catallaxy',
#             '-o',
#             'Export\\test1.csv',
#             '-a',
#             'domain=infowars.com,'
#         ]
#     )
# except SystemExit:
#     pass


from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

process.crawl('AnyDomain', 
    DOMAIN='clubtroppo.com.au', 
    MATCH="https:\\/\\/clubtroppo\\.com\\.au\\/\\d+\\/\\d+\\/\\d+\\/[\\w-]+\\/",
    CRAWL_DIFFBOT=False,
    FILE_NAME="Test_1")

# process.crawl('AnyDomain', 
#     DOMAIN='andrewelder.blogspot.com', 
#     MATCH="http:\/\/andrewelder\.blogspot\.com\/\d+\/\d+\/[\w-]+\.html",
#     CRAWL_DIFFBOT=False,
#     FILE_NAME="Test_2")

# process.crawl('AnyDomain', 
#     DOMAIN='onlineopinion.com.au', 
#     MATCH="https:\/\/onlineopinion\.com\.au\/view\.asp\?article\=\d+",
#     CRAWL_DIFFBOT=False,
#     FILE_NAME="Test_3")

process.start()