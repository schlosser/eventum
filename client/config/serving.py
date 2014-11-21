from common.interface import eventum_url_for
from flask import g


def setup_request_rules(app):
    @app.context_processor
    def modify_contex():
        """Injects a variable named ``current_user`` into all of the Jinja
        templates, so that it can be used at will.
        """
        context = {
            'eventum_url_for': eventum_url_for
        }
        if hasattr(g, 'user'):
            context['current_user'] = g.user
        return context
        return dict(hi="mom")

    @app.after_request
    def add_header(response):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response
