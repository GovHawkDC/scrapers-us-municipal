import jinja2
import os
import re
import csv
import sys
from jinja2 import Template, Environment, FileSystemLoader

# python3 utils/templates/scrapenator5000.py ~/work/local/scrapegen/sheet-out.csv

#TODO: turns out it's iqm2 not iq2m. How embarrassing.

def city_to_class(city):
    city = re.sub(r'\W+','', city)
    return city    

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

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

print("All done.")

# classname
# url
# timezone
# city_name
# ocd_id