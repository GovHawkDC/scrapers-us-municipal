import jinja2
import os
import re
import csv
import sys
import pprint
from jinja2 import Template, Environment, FileSystemLoader

# python3 utils/templates/scrapenator5000.py ~/work/local/scrapegen/sheet-out.csv

## Generate a CSV from our spreadsheet of jurisdictions and providers
# and build scraper stubs for all of them.
# the create_PROVIDER functions will load the templates/PROVIDER/ files
# and sub in the needed variables for python classname, url, ocd id, etc

# Note that most providers only get __init__ and events.py --
# only legistar offers bills right now.
# TODO: investigate municode's ordinances pages and see if that
# fits our bill model well enough

# All of the generated scrapers inherit from the base classes in 
# templates/PROVIDER.py -- that's where the real work is done.

# legistar has two different types of scraper,
# those with a public API and those without (api vs web)

#TODO: turns out it's iqm2 not iq2m. How embarrassing.

# Sub out whitespace in the city name
def city_to_class(city):
    city = re.sub(r'\W+','', city)
    return city    

# pull legistar city ID from url
def legistar_city_id(url):
    # Bodies page is a good small / quick to load API test
    # http://webapi.legistar.com/v1/<id>/bodies
    city_id = re.findall(r'\/\/(.*)\.legistar\.com', url)
    if city_id:
        city_id = city_id[0]
    return city_id

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# ignore these rows
skips = [
    'LA City'
]

def create_novusagenda(row):
    file_loader = FileSystemLoader(THIS_DIR+'/novusagenda')
    env = Environment(loader=file_loader)

    # TODO: Make sure url has novusagenda in it or skip
    city_name = row[2]
    class_name = city_to_class(city_name)
    city_lower = class_name.lower()

    # safe to lcase novusagenda urls
    url = row[5].lower()
    url = url.partition('agendapublic/')
    url = url[0] + url[1]

    output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    env.get_template('__init__.py').stream(
        city_name=city_name,
        class_name=class_name,
        url=url,
        ocd_id=row[13],
    ).dump(output_path+'/__init__.py')
    env.get_template('events.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
    ).dump(output_path+'/events.py')
    print("Generated NovusAgenda Scraper for {}".format(city_name))

def create_agendacenter(row):
    file_loader = FileSystemLoader(THIS_DIR+'/agendacenter')
    env = Environment(loader=file_loader)

    # TODO: Make sure url has novusagenda in it or skip
    city_name = row[2]
    class_name = city_to_class(city_name)
    city_lower = class_name.lower()

    url = row[5]
    # url = url.partition('agendapublic/')
    # url = url[0] + url[1]

    output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    env.get_template('__init__.py').stream(
        city_name=city_name,
        class_name=class_name,
        url=url,
        ocd_id=row[13],
    ).dump(output_path+'/__init__.py')
    env.get_template('events.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
    ).dump(output_path+'/events.py')
    print("Generated AgendaCenter Scraper for {}".format(city_name))

def create_iq2m(row):
    file_loader = FileSystemLoader(THIS_DIR+'/iq2m')
    env = Environment(loader=file_loader)

    # TODO: Make sure url has novusagenda in it or skip
    city_name = row[2]
    class_name = city_to_class(city_name)
    city_lower = class_name.lower()

    url = row[5].lower()
    url = url.partition('.iqm2.com/')
    url = url[0] + url[1]

    output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    env.get_template('__init__.py').stream(
        city_name=city_name,
        class_name=class_name,
        url=url,
        ocd_id=row[13],
    ).dump(output_path+'/__init__.py')
    env.get_template('events.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
        city_name=city_name,
    ).dump(output_path+'/events.py')
    print("Generated iq2m Scraper for {}".format(city_name))

def create_granicus(row):
    file_loader = FileSystemLoader(THIS_DIR+'/granicus')
    env = Environment(loader=file_loader)

    city_name = row[2]
    class_name = city_to_class(city_name)
    city_lower = class_name.lower()

    url = row[5]
    # url = url.partition('agendapublic/')
    # url = url[0] + url[1]

    output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    env.get_template('__init__.py').stream(
        city_name=city_name,
        class_name=class_name,
        url=url,
        ocd_id=row[13],
    ).dump(output_path+'/__init__.py')
    env.get_template('events.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
    ).dump(output_path+'/events.py')
    print("Generated Granicus Scraper for {}".format(city_name))

def create_legistar_api(row, city_id):
    file_loader = FileSystemLoader(THIS_DIR+'/legistar/api')
    env = Environment(loader=file_loader)

    city_name = row[2]
    class_name = city_to_class(city_name)
    city_lower = class_name.lower()

    url = row[5]
    # url = url.partition('agendapublic/')
    # url = url[0] + url[1]

    output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    env.get_template('__init__.py').stream(
        city_name=city_name,
        class_name=class_name,
        url=url,
        ocd_id=row[13],
        city_id=city_id,
    ).dump(output_path+'/__init__.py')

    env.get_template('events.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
        city_id=city_id,
    ).dump(output_path+'/events.py')

    env.get_template('bills.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
        city_id=city_id,
    ).dump(output_path+'/bills.py')    
    print("Generated Legistar API Scraper for {}".format(city_name))

def create_legistar_web(row):
    file_loader = FileSystemLoader(THIS_DIR+'/legistar/web')
    env = Environment(loader=file_loader)

    city_id = legistar_city_id(row[5])

    city_name = row[2]
    class_name = city_to_class(city_name)
    city_lower = class_name.lower()

    url = row[5]
    # url = url.partition('agendapublic/')
    # url = url[0] + url[1]

    output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    env.get_template('__init__.py').stream(
        city_name=city_name,
        class_name=class_name,
        url=url,
        ocd_id=row[13],
        city_id=city_id,
    ).dump(output_path+'/__init__.py')

    env.get_template('events.py').stream(
        class_name=class_name,
        url=url,
        timezone=row[14],
        city_id=city_id,
    ).dump(output_path+'/events.py')

    # env.get_template('bills.py').stream(
    #     class_name=class_name,
    #     url=url,
    #     timezone=row[14],
    #     city_id=city_id,
    # ).dump(output_path+'/bills.py')    
    print("Generated Legistar Web Scraper for {}".format(city_name))




with open(sys.argv[1], mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if row[2].lower() == 'done':
            continue

        provider = row[4].lower()
        if provider == 'novusagenda' and row[2] not in skips:
            create_novusagenda(row)
        elif provider == 'agendacenter' and row[2] not in skips:
            create_agendacenter(row)
        elif provider == 'iq2m' and row[2] not in skips:
            create_iq2m(row)
        elif provider == 'granicus' and row[2] not in skips:
            create_granicus(row)
        elif provider == 'legistar' and row[2] not in skips:
            city_id = row[22]
            if city_id:
                create_legistar_api(row, city_id)
            else:
                create_legistar_web(row)

print("All done.")

# classname
# url
# timezone
# city_name
# ocd_id