import jinja2
import os
import re
import csv
import sys
from jinja2 import Template, Environment, FileSystemLoader

# python3 utils/templates/scrapenator5000.py ~/work/local/scrapegen/sheet-out.csv

def city_to_class(city):
    city = re.sub(r'\W+','', city)
    return city    

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

file_loader = FileSystemLoader(THIS_DIR+'/novusagenda')
env = Environment(loader=file_loader)

skips = [
    'LA City'
]

with open(sys.argv[1], mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        provider = row[4].lower()
        if provider == 'novusagenda' and row[2] not in skips:
            print(row)
            city_name = row[2]
            class_name = city_to_class(city_name)
            city_lower = class_name.lower()

            url = row[5].lower()
            url = url.partition('agendapublic/')
            url = url[0] + url[1]

            output_path = '{}/../../{}'.format(THIS_DIR, city_lower)

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            env.get_template('init.py').stream(
                city_name=city_name,
                class_name=class_name,
                url=url,
                ocd_id=row[14],
            ).dump(output_path+'/__init__.py')
            env.get_template('events.py').stream(
                class_name=class_name,
                url=url,
                timezone=row[15],
            ).dump(output_path+'/events.py')


# classname
# url
# timezone
# city_name
# ocd_id