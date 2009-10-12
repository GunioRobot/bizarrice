import helpers
import view


def with_page(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, page_slug=None):
        page = None
        if page_slug is not None:
            page = helpers.get_page(page_slug)
            if page is None:
                view.Renderer().render_error(self, 404)
                return
        funct(self, page)
    return decorate

def with_post(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, year=None, month=None, day=None, slug=None):
        post = None
        if slug is not None:
            post = helpers.get_post(year, month, day, slug)
            if post is None:
                view.Renderer().render_error(self, 404)
                return
        funct(self, post)
    return decorate

