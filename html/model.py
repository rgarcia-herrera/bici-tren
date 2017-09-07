from mongoengine import *

class Bike(db.Entity):
    point = GeoPointField()
    speed = FloatField()

    # def __repr__(self):
    #     return "<bike %s %s %s>" % (self.id, self.point)


b = Bike(point=[21.1232,23.23432])
b.save()
