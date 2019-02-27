
DRIVER_TYPE='chrome'
HEADLESS=True
LOAD_PICTURE=False

#driver settings
DRIVER_SETTINGS=dict(
    phantomjs_path='/usr/bin/phantomjs2.2.1/bin/phantomjs',
    chrome_path='/usr/bin/chromedriver'
)

#mongo settings
MONGO_SETTINGS= dict(
    mongo_ip='10.245.146.37',
    mongo_port=27017,
    mongo_db='illegal_domains_profile'
)

#mysql settings
MYSQL_SETTINGS = dict(
    host="0.0.0.0",
    user="root",
    port = 3306,
    passwd="",
    db="illegal_domains_profile",
    charset="utf8"
)