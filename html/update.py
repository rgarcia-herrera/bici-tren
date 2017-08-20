from pony.orm import db_session, Database
import model
import argparse

parser = argparse.ArgumentParser(
    description='update bike agent')

parser.add_argument('--init', default=0, type=int,
                    help='0 or 1 wether to init the db')

parser.add_argument('--lon', type=float,
                    help='longitude')

parser.add_argument('--lat', type=float,
                    help='latitude')

parser.add_argument('--id', type=int, required=False,
                    help='bike id')

args = parser.parse_args()


if args.init == 1:
    model.db.bind('sqlite', 'bikes.sqlite', create_db=True)
    model.db.generate_mapping(create_tables=True)
    with db_session:
        b = model.Bike(lon=args.lon,
                       lat=args.lat)
        print b
else:
    model.db.bind('sqlite', 'bikes.sqlite', create_db=False)
    model.db.generate_mapping(create_tables=False)
    with db_session:    
        b = model.Bike[args.id]
        b.lon = args.lon
        b.lat = args.lat
        print b
