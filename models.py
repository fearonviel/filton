from google.appengine.ext import ndb

class Message(ndb.Model):
    message = ndb.StringProperty()
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    grade = ndb.StringProperty()
    deleted = ndb.BooleanProperty(default=False)
    email = ndb.StringProperty()

