# -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo

def index(): return dict()

def index_new(): return dict()

def search():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)    
    details_form=SQLFORM.factory(
        Field('category', requires=IS_EMPTY_OR(IS_IN_SET(categories))),
        Field('language', requires=IS_EMPTY_OR(IS_IN_SET(languages))),
        Field('keywords'),
        _name="detail-search",
        _class="form-horizontal"
    )
    sounds = None
    if details_form.process(formname='detail-search', message_onsuccess="").accepted:
        query = active_sounds
        if details_form.vars.language:
            query &= Sounds.language==details_form.vars.language
        if details_form.vars.category:
            query &= Sounds.category==details_form.vars.category
        if details_form.vars.keywords:
            values = details_form.vars.keywords.split(" ")
            query &= Sounds.keywords.contains(values, all=False)
        sounds = db(query).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
        paginator.records = len(sounds)
        paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
        return locals()
    
    if search_form.process(session=None, formname="master-search", message_onsuccess="").accepted and search_form.vars.query:
        values = search_form.vars.query.split(",")
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
        # display nothing if no search criteria (client's request)
        #else:
        #    sounds = db(active_sounds).select(orderby=~Sounds.created_on,
        #                                  limitby=paginator.limitby())
    if not sounds: sounds = []
    paginator.records = len(sounds)
    paginate_info = PaginateInfo(paginator.page,
                            paginator.paginate, paginator.records)
    return locals()

@auth.requires_login()
def submit_experience():
    import uuid        
    return dict(experience_uuid = str(uuid.uuid4()))
    
@auth.requires_login()
def create_experience():    
    if request.env.request_method == 'GET':        
        sound_id = Sounds.insert(uuid=a0)
        sound = Sounds(sound_id)
    else:
        sound = db(Sounds.uuid == a0).select().first()
    Sounds.is_active.default = False
    form = SQLFORM(Sounds, sound, _action=URL('default', 'create_experience', args=a0), _id="create-experience-form")    
    if form.process().accepted:
        new_sound = Sounds(form.vars.id)
        if new_sound.release_date and new_sound.release_date > request.now:                
            new_sound.update_record(is_active=False, status = T('Scheduled for') + ' ' + str(new_sound.release_date))
        response.flash = T('Upload complete!')
        redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
        response.view = 'default/create_experience_full.html'
        response.flash = T('Form has errors')    
    return locals()

def set_download_info():
    sound = db(Sounds.uuid == request.vars.uuid).select().first()    
    if not sound: return 'notfound!'    
    is_active = True
    status = T('Ready')
    if sound.release_date and sound.release_date > request.now:
        status = T('Scheduled for') + ' ' + str(sound.release_date)
        is_active = False
    sound.update_record(uuid = request.vars.uuid,
                        download_server=request.vars.host,
                        download_key=request.vars.key,
                        is_active = is_active,
                        status = status)
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
            new_sound.update_record(is_active=False, status = T('Scheduled for') + ' ' + str(new_sound.release_date))
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
    #TODO: remove from all favorites and playlists
    return locals()

@auth.requires_signature()
def my_uploads():
    paginator = Paginator(paginate=10,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)    

    sounds = db(user_sounds).select(orderby=~Sounds.created_on,
                                    limitby=paginator.limitby())
    paginator.records = len(sounds)
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    return locals()

def details():
    detail_sound = Sounds(a0) or redirect(URL('index'))
    if not detail_sound.is_active: raise HTTP(404)
    query = active_sounds & (Sounds.created_by==detail_sound.created_by)    
    detail_sound.update_record(play_count=(detail_sound.play_count or 0) + 1)

    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)    

    sounds = db(query).select(orderby=~Sounds.created_on,
                              limitby=paginator.limitby())
    paginator.records = len(sounds)
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    
    return locals()

def most_popular():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)    

    sounds = db(active_sounds).select(orderby=~Sounds.play_count,
                                      limitby=paginator.limitby())
    paginator.records = len(sounds)
    return locals()

def by_user():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)        
    
    count = Sounds.id.count()
    sounds = db(active_sounds).select(Sounds.download_server, Sounds.download_key, Sounds.created_by, count, orderby=~count,
                                      groupby=Sounds.created_by, limitby=paginator.limitby())
    paginator.records = len(sounds)
    
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    return locals()

def by_language():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)    
    
    count = Sounds.id.count()
    sounds = db(active_sounds).select(Sounds.created_by, Sounds.download_server, Sounds.download_key, Sounds.language, count, orderby=~count,
                                      groupby=Sounds.language, limitby=paginator.limitby())
    paginator.records = len(sounds)
    
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)
    return locals()

def user():    
    return dict(form=auth())

def download():
    return response.download(request,db)

def staticpage():
    if a0 in ('about', 'terms', 'howitworks', 'buy', 'faq', 'business', 'mission'):
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
            response.flash = T('Thank you')
            response.js = "jQuery('#%s').hide()" % request.cid
        else:
            form.errors.your_email = "Unable to send the email"
    return dict(form=form)

@auth.requires_signature()
def add_favorite():
    p = db(Profiles.user == auth.user_id).select().first()    
    fav = p.favorites if p and p.favorites else []
    sound = Sounds(a0) or redirect(URL('index'))
    if not sound.is_active: raise HTTP(404)
    if not sound.id in fav: fav.append(sound.id)    
    Profiles.update_or_insert(Profiles.user==auth.user_id,
                       user=auth.user_id, favorites = fav)
    return ''

@auth.requires_signature()
def remove_favorite():
    p = db(Profiles.user == auth.user_id).select().first()    
    if p:
        sound = Sounds(a0) or redirect(URL('index'))
        if not sound.is_active: raise HTTP(404)
        p.favorites.remove(sound.id)
        p.update_record()
    redirect(URL('default','favorites'))
    return dict()

@auth.requires_login()
def favorites():    
    p = db(Profiles.user == auth.user_id).select().first()    
    sounds = db(active_sounds & Sounds.id.belongs(p.favorites)).select() if p and p.favorites else []
    
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
        
    paginator.records = len(sounds)
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)    
    return locals()

@auth.requires_signature()
def add_playlist():
    p = db(Profiles.user == auth.user_id).select().first()    
    pl = p.playlist if p and p.playlist else []
    sound = Sounds(a0) or redirect(URL('index'))
    if not sound.is_active: raise HTTP(404)
    if not sound.id in pl: pl.append(sound.id)    
    Profiles.update_or_insert(Profiles.user==auth.user_id,
                       user=auth.user_id, playlist = pl)        
    return ''

@auth.requires_signature()
def remove_playlist():
    p = db(Profiles.user == auth.user_id).select().first()    
    if p:
        sound = Sounds(a0) or redirect(URL('index'))
        if not sound.is_active: raise HTTP(404)
        p.playlist.remove(sound.id)
        p.update_record()
    redirect(URL('default','playlist'))
    return dict()

@auth.requires_login()
def playlist():
    p = db(Profiles.user == auth.user_id).select().first()    
    sounds = db(active_sounds & Sounds.id.belongs(p.playlist)).select() if p and p.playlist else []
    
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v':1}, anchor='main', renderstyle=True)
        
    paginator.records = len(sounds)
    paginate_info = PaginateInfo(paginator.page,
                                 paginator.paginate, paginator.records)    
    return locals()
