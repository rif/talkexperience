def post():
    sound_id = request.args(0, cast=int, otherwise=URL('default', 'index'))
    db.comments.sound.default = sound_id
    if auth.is_logged_in():
        form = crud.create(db.comments, _action=URL('comments', 'post', args=sound_id), _id="comment-form")
    comments = db(db.comments.sound==sound_id).select()
    return locals()