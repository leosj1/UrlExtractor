import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'unz',
            '-o',
            'Export\\unz.csv',
        ]
    )
except SystemExit:
    pass