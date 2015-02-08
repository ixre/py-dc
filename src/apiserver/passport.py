from core import newdb,apibase

class passportapi(apibase):
    def GET(self):
        db=newdb();
        return db.fetchall('SELECT * FROM pt_submerchants')[0][2]   