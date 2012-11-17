# -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo

def index(): return dict()

def index_new(): return dict()

def search():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(active_sounds).count()
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    details_form=SQLFORM.factory(
        Field('category', requires=IS_IN_SET(categories)),
        Field('language', requires=IS_IN_SET(languages)),
        Field('keywords'),
        _name="detail-search",
        _class="form-horizontal"
    )
    sounds = None
    if search_form.process(session=None, formname=None, message_onsuccess="").accepted and search_form.vars.query:
        values = search_form.vars.query.split(" ")
        sounds = db(active_sounds & (
            Sounds.title.contains(values, all=False) |
            Sounds.description.contains(values, all=False) |
            Sounds.keywords.contains(values, all=False))).select(orderby=~Sounds.created_on, limitby=paginator.limitby())        
    else:
        if request.vars.user:
            sounds = db(active_sounds & (Sounds.created_by==request.vars.user)).select(orderby=~Sounds.created_on,
                                          limitby=paginator.limitby())
        elif request.vars.language:
            sounds = db(active_sounds & (Sounds.language==request.vars.language)).select(orderby=~Sounds.created_on,
                                          limitby=paginator.limitby())
        else:
            sounds = db(active_sounds).select(orderby=~Sounds.created_on,
                                          limitby=paginator.limitby())
    return locals()

def record():
    return create_sound()  

@auth.requires_login()
def create_sound():
    from os.path import splitext
    form = SQLFORM(Sounds, submit_button=T('Share'))
    pic_file = request.vars.picture
    if form.process().accepted:
        # bellow is the code that try to update the file if there was allready a file with that id
        # this was executed with dbio=False
        """sound = db(Sounds.uuid == form.vars.uuid).select().first()        
        if sound:
            if not form.vars.title: # keep the name of the file as title
                form.vars.title = sound.title
            sound.update_record(picture_file=pic_file.read_binary() if pic_file else None, **dict(form.vars))
            if sound.release_date and sound.release_date > request.now:
                sound.status = T('Scheduled for')+' '+str(sound.release_date)
                sound.is_active = False
            else:
                sound.is_active = True
                sound.status = T('Ready')
            sound.created_by = sound.modified_by = auth.user_id
            sound.update_record()
        else:            
            Sounds.insert(picture_file=pic_file.read_binary() if pic_file else None, **dict(form.vars))"""
        response.flash = T('Upload complete!')
        redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
       response.flash = T('form has errors')    
    return locals()

def set_download_info():
    # import logging
    # logger = logging.getLogger("test")
    # logger.info("sssssssssssssssssssssssssssssss")
    sound = db(Sounds.uuid == request.vars.uuid).select().first()
    if sound:
        sound.update_record(uuid = request.vars.uuid,
                            download_server=request.vars.host,
                            download_key=request.vars.key)
        if sound.release_date and sound.release_date > request.now:
            sound.status = T('Scheduled for') + ' ' + str(sound.release_date)
        else:
            sound.is_active = True
            sound.status = T('Ready')
    else:
        id = Sounds.insert(uuid = request.vars.uuid,
                           download_server=request.vars.host,
                           download_key=request.vars.key)
        sound = Sounds(id)
        if request.vars.filename:
            from os.path import splitext
            title = splitext(request.vars.filename)[0]
            sound.title = title
    sound.update_record()
    return "done!"

def activate_scheduled_sounds():
    for_activation = db((Sounds.is_active == False) & \
        (Sounds.release_date<=request.now) & \
        (Sounds.download_key!="")).select(orderby=Sounds.release_date)
    activated_sounds = 0
    for sound in for_activation:
        sound.is_active=True
        sound.status = T('Ready')
        sound.update_record()
        mail.send(to=sound.email,
                  subject='%s released a recording' % (sound.username),
                  message = sound.comments + T('\n\nYou can hear the recording here: ') + \
                  URL('details', args=sound.id, scheme=True, host=True))
        activated_sounds += 1
    return 'Activated %d sounds. (%s)' % (activated_sounds, request.now )

@auth.requires_signature()
def update_sound():
    sound = Sounds(a0) or redirect(URL('index'))
    form = SQLFORM(Sounds, sound,\
                   fields=['title',
                           'description',
                           'keywords',
                           'category',
                           'language',
                           'picture',
                           'release_date',
                           'email',
                           'is_active'],
                   showid=False)
    if form.process().accepted:
        new_sound = Sounds(form.vars.id)
        if new_sound.release_date and new_sound.release_date > request.now:
            new_sound.update_record(is_active=False)
        response.flash = T('Sound info updated!')
        redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
        response.flash = T('form has errors')
    return locals()

@auth.requires_signature()
def delete_sound():
    if request.env.web2py_runtime_gae:
        from google.appengine.api import urlfetch
        sound = Sounds(a0) or redirect(URL('index'))
        if sound.download_server and sound.download_key:
            urlfetch.fetch(sound.delete_url)
    crud.delete(Sounds, a0,
                next=URL('my_uploads', user_signature=True),
                message=T('Sound deleted!'))
    return locals()

@auth.requires_signature()
def my_uploads():
    paginator = Paginator(paginate=10,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(user_sounds).count()
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)

    sounds = db(user_sounds).select(orderby=~Sounds.created_on,
                                    limitby=paginator.limitby())
    return locals()

def details():
    detail_sound = Sounds(a0) or redirect(URL('index'))
    query = active_sounds & (Sounds.created_by==detail_sound.created_by)    
    detail_sound.update_record(play_count=(detail_sound.play_count or 0) + 1)

    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(query).count()
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)

    sounds = db(query).select(orderby=~Sounds.created_on,
                              limitby=paginator.limitby())
    return locals()

def most_popular():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
    paginator.records = db(active_sounds).count()

    sounds = db(active_sounds).select(orderby=~Sounds.play_count,
                                      limitby=paginator.limitby())
    return locals()

def by_user():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
    sounds_grouped = db(active_sounds).select(groupby=Sounds.created_by)
    paginator.records = len(sounds_grouped)
    
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    
    count = Sounds.id.count()
    sounds = db(active_sounds).select(Sounds.download_server, Sounds.download_key, Sounds.created_by, count, orderby=~count,
                                      groupby=Sounds.created_by, limitby=paginator.limitby())
    return locals()

def by_language():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
    sounds_grouped = db(active_sounds).select(groupby=Sounds.language)
    paginator.records = len(sounds_grouped)
    
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    
    count = Sounds.id.count()
    sounds = db(active_sounds).select(Sounds.created_by, Sounds.download_server, Sounds.download_key, Sounds.language, count, orderby=~count,
                                      groupby=Sounds.language, limitby=paginator.limitby())
    return locals()

def user():
    return dict(form=auth())

def download():
    return response.download(request,db)

def staticpage():
    if a0 in ('about', 'terms', 'howitworks', 'buy', 'faq', 'business'):
        response.view = 'default/%s.html' % a0
        return {}
    return ''

def contact():
    form=SQLFORM.factory(
        Field('your_name',requires=IS_NOT_EMPTY()),
        Field('your_email',requires=IS_EMAIL()),
        Field('message', 'text', requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        if mail.send(to='radu.fericean@wisebiz-group.com;gmurgan@sympatico.ca',
                  subject='from %s (%s)' % (form.vars.your_name, form.vars.your_email),
                  message = form.vars.message):
            response.flash = 'Thank you'
            response.js = "jQuery('#%s').hide()" % request.cid
        else:
            form.errors.your_email = "Unable to send the email"
    return dict(form=form)

def comments():
    return dict(sound_id=a0)
