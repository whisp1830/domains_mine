#-*- coding: utf8 -*-

DRIVER_TYPE='chrome'#chrome/phantomjs
HEADLESS=True
LOAD_PICTURE=False

#driver settings
DRIVER_SETTINGS=dict(
    phantomjs_path='/usr/phantomjs/2.1.1/bin/phantomjs',
    chrome_path='/usr/bin/chromedriver'
)

#需配置参数
DB="idomains_mine_locate"#数据库名
LOAD_SQL_TABLE="possible_illegal_domains_index" # 导出待检测域名的表名
UPDATE_SQL_TABLE="possible_illegal_domains_index" #更新检测结果表表名

#mysql settings
MYSQL_SETTINGS = dict(
    host="0.0.0.0",
    user="root",
    port = 3306,
    passwd="",
    db=DB,
    charset="utf8"
)