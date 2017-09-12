import model
import argparse

parser = argparse.ArgumentParser(
    description='update bike agent')

parser.add_argument('--lon', type=float, required=True,
                    help='longitude')

parser.add_argument('--lat', type=float, required=True,
                    help='latitude')

parser.add_argument('--id', required=True,
                    help='bike id')

args = parser.parse_args()

model.connect('mydb')

b = model.Bike.objects.with_id(args.id)
b.point=[args.lon, args.lat]
b.save()

print b
