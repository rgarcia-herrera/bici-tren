import model
import argparse

parser = argparse.ArgumentParser(
    description='update bike agent')

parser.add_argument('--lat', type=float, required=True,
                    help='latitude')

parser.add_argument('--lon', type=float, required=True,
                    help='longitude')

parser.add_argument('--dlat', type=float, required=True,
                    help='destination latitude')

parser.add_argument('--dlon', type=float, required=True,
                    help='destination longitude')

parser.add_argument('--id', default='new',
                    help='bike id')

args = parser.parse_args()

model.connect('mydb')


if args.id == 'new':
    b = model.Bike()
else:
    b = model.Bike.objects.with_id(args.id)


b.point = [args.lon, args.lat]
b.destination = [args.dlon, args.dlat]
b.update(new_point=[args.lon, args.lat])

b.save()

print b
