import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                        autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def render_base(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("blog.html", blogs=blogs)

    def get(self):
        self.render_base()

class NewPost(Handler):
    def render_newpost(self, title="", blog="", error=""):
        self.render("newpost.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            a = Blog(title = title, blog = blog)
            a.put()
            self.redirect("/blog/" + str(a.key().id()))
        else:
            error = "We need both a title and blog!"
            self.render_newpost(title, blog, error)

class ViewPostHandler(Handler):
    def get(self, blog_id):
        blog_id = Blog.get_by_id(int(blog_id))

        if blog_id:
            self.render("viewpost.html", blog_id=blog_id)
        else:
            self.response.write("ERROR")


app = webapp2.WSGIApplication([
    ('/blog', MainPage), ('/blog/newpost', NewPost), webapp2.Route('/blog/<blog_id:\d+>', ViewPostHandler)
], debug=True)
