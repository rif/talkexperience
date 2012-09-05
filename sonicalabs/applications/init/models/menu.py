# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = 'Voice Your Experience'
response.subtitle = T('')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Radu Fericean <radu.fericean@wisebiz-group.com>'
response.meta.description = 'Talkexperience is a webapp for sounds/audio storage and presentation'
response.meta.keywords = 'audio, sound, music, record sound, sharing'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = 'UA-10073547-8'

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default','index'), [])
    ]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu+=[
        (SPAN('Explore'),False, None, [
                (T('Upload an Experience'),False,URL('default','create_sound')),
                (T('Record an Experience'),False,URL('default','record')),
                (T('My Experiences'),False,URL('default','my_uploads', user_signature=True)),
                ]
         )]
_()
