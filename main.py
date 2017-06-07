#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Message
import cgi
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}

        user = users.get_current_user()
        params["user"] = user

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
        else:
            logged_in = False
            login_url = users.create_login_url('/')
            params["login_url"] = login_url

        params["logged_in"] = logged_in

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("home.html")


class NewmessageHandler(BaseHandler):
    def get(self):
        return self.render_template("newmessage.html")


class RezultatHandler(BaseHandler):
    def post(self):
        newmessage = cgi.escape(self.request.get("message"))
        name = cgi.escape(self.request.get("name"))
        grade = cgi.escape(self.request.get("grade"))
        email = users.get_current_user().email()

        if not name:
            name = "Anonymous"

        if not grade:
            grade = "no grade was given"

        message = Message(message=newmessage, name=name, grade=grade, email=email)
        message.put()

        return self.redirect_to("messages")


class MessagesHandler(BaseHandler):
    def get(self):

        messages = Message.query(Message.deleted == False).order(-Message.date).fetch()
        logout_url = users.create_logout_url('/')
        params = {"messages": messages, "logout_url": logout_url}

        return self.render_template("messages.html", params=params)


class SingleMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        logout_url = users.create_logout_url('/')
        params = {"message": message, "logout_url": logout_url}
        return self.render_template("single_message.html", params=params)


class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("edit_message.html", params=params)

    def post(self, message_id):
        newmessage = cgi.escape(self.request.get("message"))
        name = cgi.escape(self.request.get("name"))
        grade = cgi.escape(self.request.get("grade"))

        if not grade:
            grade = "no grade was given"

        message = Message.get_by_id(int(message_id))
        message.message = newmessage
        message.name = name
        message.grade = grade
        message.put()

        return self.redirect_to("messages")


class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("delete_message.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.deleted = True
        message.put()
        return self.redirect_to("messages")


class DeletedMessagesHandler(BaseHandler):
    def get(self):

        messages = Message.query(Message.deleted == True).order(-Message.date).fetch()
        logout_url = users.create_logout_url('/')
        params = {"messages": messages, "logout_url": logout_url}

        return self.render_template("deleted_messages.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/messages', MessagesHandler, name="messages"),
    webapp2.Route('/newmessage', NewmessageHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/message/<message_id:\d+>', SingleMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/edit', EditMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', DeleteMessageHandler),
    webapp2.Route('/deletedmessages', DeletedMessagesHandler)
], debug=True)
