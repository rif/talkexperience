# -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo

def index(): return dict()

def index_real():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,  extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(active_sounds).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    form = SQLFORM.factory(Field('query', default=T('Search')))

    sounds = None
    if form.process(message_onsuccess="").accepted and form.vars.query:
        values = form.vars.query
        sounds = db(active_sounds).select(orderby=~Sounds.created_on,
            limitby=paginator.limitby()).find(lambda s: values.lower() in s.title.lower() or \
             values.lower() in s.description.lower() or values.lower() in s.keywords.lower())
    else:
        sounds = db(active_sounds).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
    return locals()

@auth.requires_login()
def record():
    return locals()

@auth.requires_login()
def create_sound():
    from os.path import splitext
    form = SQLFORM(Sounds, submit_button=T('Share'))
    if form.process(dbio=False).accepted:
        sound = db(Sounds.uuid == form.vars.uuid).select().first()
        if sound:
            if not form.vars.title: # keep the name of the file as title
                form.vars.title = sound.title
            sound.update_record(**dict(form.vars))
            if sound.release_date and sound.release_date > request.now:
                sound.status = T('Scheduled for') + ' ' + str(sound.release_date)
                sound.is_active = False
            else:
                sound.is_active = True
                sound.status = T('Ready')
            sound.created_by = sound.modified_by = auth.user_id
            sound.update_record()
        else:
            Sounds.insert(**dict(form.vars))
        response.flash = T('Upload complete!')
        redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
       response.flash = T('form has errors')
    response.subtitle='Upload Your Experience'
    return locals()

def set_download_info():
    # import logging
    # logger = logging.getLogger("test")
    # logger.info("sssssssssssssssssssssssssssssss")
    sound = db(Sounds.uuid == request.vars.uuid).select().first()
    if sound:
        sound.update_record(uuid = request.vars.uuid, download_server=request.vars.host, download_key=request.vars.key)
        if sound.release_date and sound.release_date > request.now:
            sound.status = T('Scheduled for') + ' ' + str(sound.release_date)
        else:
            sound.is_active = True
            sound.status = T('Ready')
    else:
        id = Sounds.insert(uuid = request.vars.uuid, download_server=request.vars.host, download_key=request.vars.key)
        sound = Sounds(id)
        from os.path import splitext
        title = splitext(request.vars.filename)[0]
        sound.title = title
    sound.update_record()
    return "done!"

def activate_scheduled_sounds():
    for_activation = db((Sounds.is_active == False) & (Sounds.release_date <= request.now)).select(orderby=Sounds.release_date)
    activated_sounds = 0
    for sound in for_activation:
        sound.is_active=True
        sound.status = T('Ready')
        sound.update_record()
        mail.send(to=sound.email, subject='%s released a recording' % (sound.username),
            message = T('You can check the recording here: ') + URL('details', args=sound.id, scheme=True, host=True))
        activated_sounds += 1
    return 'Activated %d sounds. (%s)' % (activated_sounds, request.now )

@auth.requires_login()
@auth.requires_signature()
def update_sound():
    sound = Sounds(a0) or redirect(URL('index'))
    form = SQLFORM(Sounds, sound, fields=['title', 'description', 'keywords', 'language', 'price', 'release_date', 'email' , 'is_active'], showid=False)
    if form.process().accepted:
        new_sound = Sounds(form.vars.id)
        if new_sound.release_date and new_sound.release_date > request.now:
            new_sound.update_record(is_active=False)
        response.flash = T('Sound info updated!')
        redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
        response.flash = T('form has errors')
    return locals()

@auth.requires_login()
@auth.requires_signature()
def delete_sound():
    if request.env.web2py_runtime_gae:
        from google.appengine.api import urlfetch
        sound = Sounds(a0) or redirect(URL('index'))
        urlfetch.fetch(sound.delete_url)
    crud.delete(Sounds, a0, next=URL('my_uploads', user_signature=True), message=T('Sound deleted!'))
    return locals()

@auth.requires_login()
@auth.requires_signature()
def my_uploads():
    paginator = Paginator(paginate=10, extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(user_sounds).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    sounds = db(user_sounds).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
    return locals()

def details():
    detail_sound = Sounds(a0) or redirect(URL('index'))
    query = active_sounds & (Sounds.created_by==detail_sound.created_by)
    new_count = detail_sound.play_count or 0 + 1
    detail_sound.update_record(play_count=new_count)

    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate, extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(query).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    sounds = db(query).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
    return locals()

def most_popular():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate, extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(active_sounds).count()

    sounds = db(active_sounds).select(orderby=~Sounds.play_count, limitby=paginator.limitby())
    return locals()

def user():
    return dict(form=auth())


def download():
    return response.download(request,db)

def about():
    return dict()

def terms():
    return dict()

def howitworks():
    return dict()

def contact():
    form=SQLFORM.factory(
        Field('your_name',requires=IS_NOT_EMPTY()),
        Field('your_email',requires=IS_EMAIL()),
        Field('message', 'text', requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        if mail.send(to='radu.fericean@wisebiz-group.com;gmurgan@sympatico.ca;teodor.giles@wisebiz-group.com',
                  subject='from %s (%s)' % (form.vars.your_name, form.vars.your_email),
                  message = form.vars.message):
            response.flash = 'Thank you'
            response.js = "jQuery('#%s').hide()" % request.cid
        else:
            form.errors.your_email = "Unable to send the email"
    return dict(form=form)

def buy():
    return dict()
