Comments = db.define_table('comments',
    Field('sound', 'reference sounds', readable=False, writable=False),
    Field('body','text',label='Your comment'),
    auth.signature
)
