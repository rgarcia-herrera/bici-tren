from mongoengine import Document, connect, GeoPointField, FloatField



class Bike(Document):
    point = GeoPointField()
    speed = FloatField()

    def __str__(self):
        return "<bike %s %s>" % (self.id, self.point)

