#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import cgi
from google.appengine.ext import db
from webapp2_extras import routes

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def get_posts(lim, off):
    """
    Method to get only limit number of items starting from offset from the db
    """
    query = Content.all().order('-created')
    return query.fetch(limit=lim, offset=off)
class Content(db.Model):
    """
    Content DB class
    """
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
class MainHandler(webapp2.RequestHandler):
    """
    Class to handle Blog pages
    """
    def render_home(self, title="", contents="", prev_page="", next_page=""):
        page = self.request.get("page")
        page_limit = 5
        offset = 0
        page = page and int(page)
        if page:
            offset = (page-1)*page_limit
        else:
            page = 1
        contents = get_posts(int(page_limit), int(offset))
        prev_page = None
        next_page = None
        if page > 1:
            prev_page = page - 1
        if len(contents) == page_limit and Content.all().count() > offset+page_limit:
            next_page = page + 1
        t = jinja_env.get_template("post.html")
        response = t.render(title=title, contents=contents, prev_page=prev_page, next_page=next_page)
        self.response.out.write(response)

    def get(self):
        self.render_home()

class NewpostHandler(webapp2.RequestHandler):
    """
        Handles requests coming in to '/newpost'
    """
    def get(self):
        """
        Method to render newpost
        """
        # render the newpost template
        t = jinja_env.get_template("newpost.html")
        self.response.out.write(t.render())

    def post(self):
        """
        Method to render for Title and Content
        """
        error = "Must have Title and Content"
        title = self.request.get("title")
        content = self.request.get("content")

        t = jinja_env.get_template("newpost.html")

        if title and content:
            a = Content(title=title, content=content)
            a.put()
            self.redirect('/blog/%d' % a.key().id())
        else:
            self.response.out.write(t.render(title=title, error=error))

class ViewPostHandler(webapp2.RequestHandler):
    """
     Handles requests coming in to webapp2.Route('/blog/<id:\d+>')
    """
    def get(self, id):
        content = Content.get_by_id(int(id))
        t = jinja_env.get_template("post.html")
        if content:
            page = t.render(contents=[content])
            self.response.out.write(page)
        else:
            # If post is not found... Displays error
            error = "This blog entry does NOT exist"
            self.response.out.write(error)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewpostHandler),
    ('/blog', MainHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
