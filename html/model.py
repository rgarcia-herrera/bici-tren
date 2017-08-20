from pony.orm import db_session, Database, Required, Json
from decimal import Decimal

db = Database()

class Bike(db.Entity):
    # tags = Required(Json)
    lon = Required(Decimal)
    lat = Required(Decimal)

    def __repr__(self):
        return "<bike %s %s %s>" % (self.id, self.lon, self.lat)
