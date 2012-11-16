@auth.requires_login()
def post():
    sound_id = request.args(0, cast=int, otherwise=URL('default', 'index'))
    db.comments.sound.default = sound_id
    return dict(form=crud.create(db.comments, _action=URL('comments', 'post', args=sound_id), _id="comment-form"),
                comments=db(db.comments.sound==sound_id).select())