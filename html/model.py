from pony.orm import db_session, Database, Required, Json

db = Database()

class Bike(db.Entity):
    # tags = Required(Json)
    lon = Required(float)
    lat = Required(float)
    
    def __repr__(self):
        return "<bike %s %s %s>" % (self.id, self.lon, self.lat)
