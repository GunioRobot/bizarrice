from google.appengine.ext import webapp

import view


class Error404Handler(webapp.RequestHandler):

    def get(self):
        renderer = view.Renderer()
        renderer.render_error(self, 404)
