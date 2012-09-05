# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    db = DAL('sqlite://storage.sqlite', migrate_enabled=True)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore', migrate_enabled=False)
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables()#(username=False, signature=False)

## configure email
mail=auth.settings.mailer
mail.settings.server =  'gae'
mail.settings.sender = 'fericean@gmail.com'
#mail.settings.login = 'user:pass'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

# if request.env.web2py_runtime_gae:            # if running on Google App Engine
#     from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
#     auth.settings.login_form = GaeGoogleAccount()
#     #auth.settings.actions_disabled.append('profile')

from gravatar import Gravatar

def get_username(row):
    u = db.auth_user(row.sounds.created_by)
    return u.first_name + ' ' + u.last_name if u else T("Anonymous")

def get_email(row):
    u = db.auth_user(row.sounds.created_by)
    return u.email if u else T("anonymous@mailinator.com")

def get_download_url(row):
    if row.sounds.download_server and row.sounds.download_server:
        return 'http://' + row.sounds.download_server + '/serve/?blobKey=' + row.sounds.download_key
    else:
        return '.'

def get_delete_url(row):
    if row.sounds.download_server and row.sounds.download_server:
        return 'http://' + row.sounds.download_server + '/delete/?blobKey=' + row.sounds.download_key
    else:
        return '.'

#languages = [u'Qaf\xe1r af', u'\u0410\u04a7\u0441\u0443\u0430', u'Ac\xe8h', u'Afrikaans', u'Akan', u'Geg\xeb', u'Alemannisch', u'\u12a0\u121b\u122d\u129b', u'Aragon\xe9s', u'\xc6nglisc', u'\u0905\u0919\u094d\u0917\u093f\u0915\u093e', u'\u0627\u0644\u0639\u0631\u0628\u064a\u0629', u'\u0710\u072a\u0721\u071d\u0710', u'Mapudungun', u'Ma\u0121ribi', u'\u0645\u0635\u0631\u0649', u'\u0985\u09b8\u09ae\u09c0\u09af\u09bc\u09be', u'Asturianu', u'\u0410\u0432\u0430\u0440', u'Kotava', u'Aymar aru', u'Az\u0259rbaycanca', u'\u0411\u0430\u0448\u04a1\u043e\u0440\u0442\u0441\u0430', u'Boarisch', u'\u017demait\u0117\u0161ka', u'\u0628\u0644\u0648\u0686\u06cc \u0645\u06a9\u0631\u0627\u0646\u06cc', u'Bikol Central', u'\u0411\u0435\u043b\u0430\u0440\u0443\u0441\u043a\u0430\u044f', u'\u0411\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438', u'\u092d\u094b\u091c\u092a\u0941\u0930\u0940', u'\u092d\u094b\u091c\u092a\u0941\u0930\u0940', u'Bislama', u'Bahasa Banjar', u'Bamanankan', u'\u09ac\u09be\u0982\u09b2\u09be', u'\u0f56\u0f7c\u0f51\u0f0b\u0f61\u0f72\u0f42', u'\u0987\u09ae\u09be\u09b0 \u09a0\u09be\u09b0/\u09ac\u09bf\u09b7\u09cd\u09a3\u09c1\u09aa\u09cd\u09b0\u09bf\u09af\u09bc\u09be \u09ae\u09a3\u09bf\u09aa\u09c1\u09b0\u09c0', u'\u0628\u062e\u062a\u064a\u0627\u0631\u064a', u'Brezhoneg', u'Br\xe1hu\xed', u'Bosanski', u'\u1a05\u1a14 \u1a15\u1a18\u1a01\u1a17', u'\u0411\u0443\u0440\u044f\u0430\u0434', u'Catal\xe0', u'Chavacano de Zamboanga', u'M\xecng-d\u0115\u0324ng-ng\u1e73\u0304', u'\u041d\u043e\u0445\u0447\u0438\u0439\u043d', u'Cebuano', u'Chamoru', u'Choctaw', u'\u13e3\u13b3\u13a9', u'Tsets\xeahest\xe2hese', u'\u06a9\u0648\u0631\u062f\u06cc', u'Corsu', u'Capice\xf1o', u'N\u0113hiyaw\u0113win / \u14c0\u1426\u1403\u152d\u140d\u140f\u1423', u'Q\u0131r\u0131mtatarca', u'\u010cesky', u'Kasz\xebbsczi', u'\u0421\u043b\u043e\u0432\u0463\u0301\u043d\u044c\u0441\u043a\u044a / \u2c14\u2c0e\u2c11\u2c02\u2c21\u2c10\u2c20\u2c14\u2c0d\u2c1f', u'\u0427\u04d1\u0432\u0430\u0448\u043b\u0430', u'Cymraeg', u'Dansk', u'Deutsch', u'\xd6sterreichisches Deutsch', u'Schweizer Hochdeutsch', u'Zazaki', u'Dolnoserbski', u'Dusun Bundu-liwan', u'\u078b\u07a8\u0788\u07ac\u0780\u07a8\u0784\u07a6\u0790\u07b0', u'\u0f47\u0f7c\u0f44\u0f0b\u0f41', u'E\u028begbe', u'\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac', u'Emili\xe0n e rumagn\xf2l', u'English', u'British English', u'Esperanto', u'Espa\xf1ol', u'Eesti', u'Euskara', u'Estreme\xf1u', u'\u0641\u0627\u0631\u0633\u06cc', u'Fulfulde', u'Suomi', u'V\xf5ro', u'Na Vosa Vakaviti', u'F\xf8royskt', u'Fran\xe7ais', u'Fran\xe7ais cadien', u'Arpetan', u'Nordfriisk', u'Furlan', u'Frysk', u'Gaeilge', u'Gagauz', u'\u8d1b\u8a9e', u'G\xe0idhlig', u'Galego', u'\u06af\u06cc\u0644\u06a9\u06cc', u'Ava\xf1e\\', u'\U00010332\U0001033f\U00010344\U00010339\U00010343\U0001033a', u'\u1f08\u03c1\u03c7\u03b1\u03af\u03b1 \u1f11\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u1f74', u'Alemannisch', u'\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0', u'Gaelg', u'\u0647\u064e\u0648\u064f\u0633\u064e', u'Hak-k\xe2-fa', u'Hawai`i', u'\u05e2\u05d1\u05e8\u05d9\u05ea', u'\u0939\u093f\u0928\u094d\u0926\u0940', u'Fiji Hindi', u'Fiji Hindi', u'Ilonggo', u'Hiri Motu', u'Hrvatski', u'Hornjoserbsce', u'Krey\xf2l ayisyen', u'Magyar', u'\u0540\u0561\u0575\u0565\u0580\u0565\u0576', u'Otsiherero', u'Interlingua', u'Bahasa Indonesia', u'Interlingue', u'Igbo', u'\ua187\ua259', u'I\xf1upiak', u'\u1403\u14c4\u1483\u144e\u1450\u1466', u'inuktitut', u'Ilokano', u'\u0413\u0406\u0430\u043b\u0433\u0406\u0430\u0439 \u011eal\u011faj', u'Ido', u'\xcdslenska', u'Italiano', u'\u1403\u14c4\u1483\u144e\u1450\u1466/inuktitut', u'\u65e5\u672c\u8a9e', u'Patois', u'Lojban', u'Jysk', u'Basa Jawa', u'\u10e5\u10d0\u10e0\u10d7\u10e3\u10da\u10d8', u'Qaraqalpaqsha', u'Taqbaylit', u'\u0410\u0434\u044b\u0433\u044d\u0431\u0437\u044d', u'\u0410\u0434\u044b\u0433\u044d\u0431\u0437\u044d', u'Kongo', u'\u06a9\u06be\u0648\u0627\u0631', u'G\u0129k\u0169y\u0169', u'K\u0131rmancki', u'Kwanyama', u'\u049a\u0430\u0437\u0430\u049b\u0448\u0430', u'Kalaallisut', u'\u1797\u17b6\u179f\u17b6\u1781\u17d2\u1798\u17c2\u179a', u'\u0c95\u0ca8\u0ccd\u0ca8\u0ca1', u'\ud55c\uad6d\uc5b4', u'\ud55c\uad6d\uc5b4 (\uc870\uc120)', u'\u041f\u0435\u0440\u0435\u043c \u041a\u043e\u043c\u0438', u'Kanuri', u'\u041a\u044a\u0430\u0440\u0430\u0447\u0430\u0439-\u041c\u0430\u043b\u043a\u044a\u0430\u0440', u'Krio', u'Kinaray-a', u'\u0915\u0936\u094d\u092e\u0940\u0930\u0940 - (\u0643\u0634\u0645\u064a\u0631\u064a)', u'\u0643\u0634\u0645\u064a\u0631\u064a', u'\u0915\u0936\u094d\u092e\u0940\u0930\u0940', u'Ripoarisch', u'Kurd\xee', u'\u041a\u043e\u043c\u0438', u'Kernowek', u'\u041a\u044b\u0440\u0433\u044b\u0437\u0447\u0430', u'Latina', u'Ladino', u'L\xebtzebuergesch', u'\u041b\u0430\u043a\u043a\u0443', u'\u041b\u0435\u0437\u0433\u0438', u'Lingua Franca Nova', u'Luganda', u'Limburgs', u'Ligure', u'L\u012bv\xf5 k\u0113\u013c', u'Lumbaart', u'Ling\xe1la', u'\u0ea5\u0eb2\u0ea7', u'Silozi', u'Lietuvi\u0173', u'Latga\u013cu', u'Latvie\u0161u', u'\u6587\u8a00', u'Lazuri', u'\u092e\u0948\u0925\u093f\u0932\u0940', u'Basa Banyumasan', u'\u041c\u043e\u043a\u0448\u0435\u043d\u044c', u'Malagasy', u'Ebon', u'\u041e\u043b\u044b\u043a \u041c\u0430\u0440\u0438\u0439', u'M\u0101ori', u'Baso Minangkabau', u'\u041c\u0430\u043a\u0435\u0434\u043e\u043d\u0441\u043a\u0438', u'\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02', u'\u041c\u043e\u043d\u0433\u043e\u043b', u'\u041c\u043e\u043b\u0434\u043e\u0432\u0435\u043d\u044f\u0441\u043a\u044d', u'\u092e\u0930\u093e\u0920\u0940', u'\u041a\u044b\u0440\u044b\u043a \u043c\u0430\u0440\u044b', u'Bahasa Melayu', u'Malti', u'Mvskoke', u'Mirand\xe9s', u'\u1019\u103c\u1014\u103a\u1019\u102c\u1018\u102c\u101e\u102c', u'\u042d\u0440\u0437\u044f\u043d\u044c', u'\u0645\u0627\u0632\u0650\u0631\u0648\u0646\u06cc', u'Dorerin Naoero', u'N\u0101huatl', u'B\xe2n-l\xe2m-g\xfa', u'Nnapulitano', u'Plattd\xfc\xfctsch', u'Nedersaksisch', u'\u0928\u0947\u092a\u093e\u0932\u0940', u'\u0928\u0947\u092a\u093e\u0932 \u092d\u093e\u0937\u093e', u'Oshiwambo', u'Niu\u0113', u'Nederlands', u'Novial', u'Nouormand', u'Sesotho sa Leboa', u'Din\xe9 bizaad', u'Chi-Chewa', u'Occitan', u'Oromoo', u'\u0b13\u0b21\u0b3c\u0b3f\u0b06', u'\u0418\u0440\u043e\u043d', u'\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40', u'Pangasinan', u'Kapampangan', u'Papiamentu', u'Picard', u'Deitsch', u'Plautdietsch', u'P\xe4lzisch', u'\u092a\u093e\u093f\u0934', u'Norfuk / Pitkern', u'Polski', u'Piemont\xe8is', u'\u067e\u0646\u062c\u0627\u0628\u06cc', u'\u03a0\u03bf\u03bd\u03c4\u03b9\u03b1\u03ba\u03ac', u'Pr\u016bsiskan', u'\u067e\u069a\u062a\u0648', u'Portugu\xeas', u'Portugu\xeas do Brasil', u'Runa Simi', u'Runa shimi', u'Rumagn\xf4l', u'Tarifit', u'Rumantsch', u'Romani', u'Kirundi', u'Rom\xe2n\u0103', u'Arm\xe3neashce', u'Tarand\xedne', u'\u0420\u0443\u0441\u0441\u043a\u0438\u0439', u'\u0420\u0443\u0441\u0438\u043d\u044c\u0441\u043a\u044b\u0439', u'Arm\xe3neashce', u'Vl\u0103he\u015fte', u'\u0412\u043b\u0430\u0445\u0435\u0441\u0442\u0435', u'\u0392\u03bb\u03b1\u03b5\u03c3\u03c4\u03b5', u'Vl\u0103he\u015fte', u'Kinyarwanda', u'\u0938\u0902\u0938\u094d\u0915\u0943\u0924', u'\u0421\u0430\u0445\u0430 \u0442\u044b\u043b\u0430', u'Sardu', u'Sicilianu', u'Scots', u'\u0633\u0646\u068c\u064a', u'Sassaresu', u'S\xe1megiella', u'Cmique Itom', u'S\xe4ng\xf6', u'\u017demait\u0117\u0161ka', u'Srpskohrvatski / \u0421\u0440\u043f\u0441\u043a\u043e\u0445\u0440\u0432\u0430\u0442\u0441\u043a\u0438', u'Ta\u0161l\u1e25iyt', u'\u0dc3\u0dd2\u0d82\u0dc4\u0dbd', u'Simple English', u'Sloven\u010dina', u'Sloven\u0161\u010dina', u'Schl\xe4sch', u'Gagana Samoa', u'\xc5arjelsaemien', u'chiShona', u'Soomaaliga', u'Shqip', u'\u0421\u0440\u043f\u0441\u043a\u0438 / Srpski', u'Sranantongo', u'SiSwati', u'Sesotho', u'Seeltersk', u'Basa Sunda', u'Svenska', u'Kiswahili', u'\u015al\u016fnski', u'\u0ba4\u0bae\u0bbf\u0bb4\u0bcd', u'\u0ca4\u0cc1\u0cb3\u0cc1', u'\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41', u'Tetun', u'\u0422\u043e\u04b7\u0438\u043a\u04e3', u'\u0422\u043e\u04b7\u0438\u043a\u04e3', u'tojik\u012b', u'\u0e44\u0e17\u0e22', u'\u1275\u130d\u122d\u129b', u'T\xfcrkmen\xe7e', u'Tagalog', u'Setswana', u'lea faka-Tonga', u'Toki Pona', u'Tok Pisin', u'T\xfcrk\xe7e', u'Xitsonga', u'\u0422\u0430\u0442\u0430\u0440\u0447\u0430/Tatar\xe7a', u'\u0422\u0430\u0442\u0430\u0440\u0447\u0430', u'Tatar\xe7a', u'chiTumbuka', u'Twi', u'Reo M\u0101`ohi', u'\u0422\u044b\u0432\u0430 \u0434\u044b\u043b', u'\u0423\u0434\u043c\u0443\u0440\u0442', u'\u0626\u06c7\u064a\u063a\u06c7\u0631\u0686\u06d5 / Uyghurche\u200e', u'\u0626\u06c7\u064a\u063a\u06c7\u0631\u0686\u06d5', u'Uyghurche\u200e', u'\u0423\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430', u'\u0627\u0631\u062f\u0648', u'O\\', u'Tshivenda', u'V\xe8neto', u'Vepsan kel\\', u'Ti\u1ebfng Vi\u1ec7t', u'West-Vlams', u'Mainfr\xe4nkisch', u'Volap\xfck', u'Va\u010f\u010fa', u'V\xf5ro', u'Walon', u'Winaray', u'Wolof', u'\u5434\u8bed', u'\u0425\u0430\u043b\u044c\u043c\u0433', u'isiXhosa', u'\u10db\u10d0\u10e0\u10d2\u10d0\u10da\u10e3\u10e0\u10d8', u'\u05d9\u05d9\u05b4\u05d3\u05d9\u05e9', u'Yor\xf9b\xe1', u'\u7cb5\u8a9e', u'Vahcuengh', u'Ze\xeauws', u'\u4e2d\u6587', u'\u6587\u8a00', u'B\xe2n-l\xe2m-g\xfa', u'\u7cb5\u8a9e', u'isiZulu']
#languages = [u'\u0410\u0431\u044b\u0437\u0448\u04d9\u0430', u'Taal', u'Gjuh\xeb', u'\u124b\u1295\u124b', u'\u0627\u0644\u0644\u063a\u0629', u'\u0720\u072b\u0722\u0710', u'Cezugun', u'\u0627\u0644\u0644\u063a\u0629', u'Llingua', u'Dil', u'\u0422\u044b\u0448\u04a1\u044b \u043a\u04af\u0440\u0435\u043d\u0435\u0448\u0442\u04d9 \u04a1\u0443\u043b\u043b\u0430\u043d\u044b\u043b\u0493\u0430\u043d \u0442\u0435\u043b:', u'Sprooch', u'\u041c\u043e\u0432\u0430', u'\u0415\u0437\u0438\u043a', u'\u09ad\u09be\u09b7\u09be', u'\u0f66\u0f90\u0f51\u0f0b\u0f62\u0f72\u0f42\u0f66\u0f0d', u'Yezh', u'Jezik', u'\u0425\u044d\u043b\u044d\u043d', u'Idioma', u'\u0632\u0645\u0627\u0646', u'Jazyk', u'J\xe3z\xebk', u'\u0469\ua641\ua651\u0301\u043a\u044a', u'Iaith', u'Sprog', u'Sprache', u'R\u011bc', u'Gbe', u'\u0393\u03bb\u03ce\u03c3\u03c3\u03b1', u'Lingvo', u'Idioma', u'Keel', u'Hizkuntza', u'Palra', u'\u0632\u0628\u0627\u0646', u'Kieli', u'Langue', u'Lengoua', u'C\xe0nan', u'Lingua', u'\u0393\u03bb\u1ff6\u03c4\u03c4\u03b1', u'Sproch', u'\xc7hengey', u'\u02bb\u014clelo', u'\u05e9\u05e4\u05d4', u'\u092d\u093e\u0937\u093e', u'Jezik', u'R\u011b\u010d', u'Nyelv', u'Lingua', u'Bahasa', u'Linguo', u'Tungum\xe1l', u'Lingua', u'\u8a00\u8a9e\u9078\u629e', u'Basa', u'\u10d4\u10dc\u10d0', u'\u062a\u0678\u0644', u'\u0422\u0456\u043b', u'Til', u'Oqaatsit', u'\u1797\u17b6\u179f\u17b6', u'\u0cad\u0cbe\u0cb7\u0cc6', u'\uc5b8\uc5b4', u'Sproch', u'Ziman', u'Yeth', u'Lingua', u'Sprooch', u'Lulimi', u'Taal', u'Kalba', u'Vol\u016bda', u'\u0408\u0430\u0437\u0438\u043a', u'\u0d2d\u0d3e\u0d37', u'\u0425\u044d\u043b', u'\u092d\u093e\u0937\u093e', u'Bahasa', u'Lingwa', u'\u041a\u0435\u043b\u044c', u'Tl\xe2t\xf2lli', u'Spraak', u'Taal', u'Spr\xe5k', u'Spr\xe5k', u'Polelo', u'Lenga', u'\xc6\u0432\u0437\u0430\u0433', u'\u0a2d\u0a3e\u0a38\u0a3c\u0a3e:', u'Schprooch', u'J\u0119zyk', u'Lenga', u'\u0698\u0628\u0647', u'L\xedngua', u'L\xedngua', u'Rimay', u'Limb\u0103', u'L\xe8nghe', u'\u042f\u0437\u044b\u043a', u'\u042f\u0437\u044b\u043a', u'\u041e\u043c\u0443\u043a \u0442\u044b\u043b\u0430', u'tutlayt', u'\u0db7\u0dcf\u0dc2\u0dcf\u0dc0', u'Jazyk', u'Jezik', u'Sproache', u'\u0408\u0435\u0437\u0438\u043a', u'Jezik', u'Sproake', u'Basa', u'Spr\xe5k', u'\u0bae\u0bca\u0bb4\u0bbf', u'\u0c2d\u0c3e\u0c37', u'Lian', u'\u0417\u0430\u0431\u043e\u043d', u'Zabon', u'\u0e20\u0e32\u0e29\u0e32', u'Dil', u'Wika', u'Dil', u'\u0422\u0435\u043b', u'Til', u'\u041c\u043e\u0432\u0430', u'Lengua', u'Kel\u2019', u'Ng\xf4n ng\u1eef', u'P\xfck', u'\u05e9\u05e4\u05e8\u05d0\u05b7\u05da', u'\u8a9e\u8a00', u'\u8bed\u8a00', u'\u8a9e\u8a00']
languages = [u'Abkhaz', u'Afar', u'Akan', u'Albanian', u'Alsatian', u'Amharic', u'Arabic', u'Aragonese', u'Armenian', u'Assamese', u'Avaric', u'Avestan', u'Aymara', u'Azerbaijani', u'Bambara', u'Bashkir', u'Basque', u'Belarusian', u'Bengali', u'Bhojpuri', u'Magahi', u'Maithili', u'Banjar', u'Indonesian', u'Bosnian', u'Breton', u'Bulgarian', u'Burmese', u'Catalan', u'Chamorro', u'Chechen', u'Chinese', u'Chuvash', u'Cornish', u'Corsican', u'Cree', u'Croatian', u'Czech', u'Danish', u'Indonesian', u'Dutch', u'English', u'Estonian', u'Ewe', u'Faroese', u'Fijian', u'Finnish', u'French', u'Fula', u'Galician', u'Georgian', u'German', u'Greek', u'Guarani', u'Gujarati', u'Haitian', u'Hausa', u'Hebrew', u'Herero', u'Hiri Motu', u'Hungarian', u'Indonesian', u'Occidental', u'Irish', u'Igbo', u'Icelandic', u'Italian', u'Japanese', u'Javanese', u'Kanuri', u'Kashmiri', u'Kazakh', u'Khmer', u'Kikuyu', u'Kyrgyz language', u'Komi', u'Kongo', u'Korean', u'Kurdish', u'Luxembourgish', u'Limburgish', u'Lingala', u'Lao', u'Lithuanian', u'Latvian', u'Manx', u'Macedonian', u'Malagasy', u'Malay', u'Standard Malay', u'Indonesian', u'Maltese', u'Maori', u'Marathi', u'Marshallese', u'Mongolian', u'Nauru', u'Navajo', u'North Ndebele', u'Nepali', u'Norwegian', u'Nuosu', u'South Ndebele', u'Occitan', u'Ojibwe', u'Oromo', u'Oriya', u'Ossetian', u'Panjabi', u'Persian', u'Polish', u'Pashto', u'Portuguese', u'Romansh', u'Romanian', u'Russian', u'Sardinian', u'Sindhi', u'Samoan', u'Sango', u'Serbian', u'Shona', u'Sinhala', u'Slovak', u'Slovene', u'Somali', u'Southern Sotho', u'Spanish', u'Sundanese', u'Swahili', u'Swedish', u'Tamil', u'Telugu', u'Tajik', u'Thai', u'Tigrinya', u'Turkmen', u'Tagalog', u'Filipino', u'Tswana', u'Tonga', u'Turkish', u'Tsonga', u'Tatar', u'Tahitian', u'Uighur', u'Ukrainian', u'Uzbek', u'Venda', u'Vietnamese', u'Walloon', u'Welsh', u'Wolof', u'Western Frisian', u'Xhosa', u'Yiddish', u'Yoruba', u'Zulu']

import uuid

Sounds = db.define_table("sounds",
    Field('title'),
    Field('description', 'text'),
    Field('keywords', comment=T('Comma separated key words')),
    Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
    Field('download_server', writable=False, readable=False),
    Field('download_key', writable=False, readable=False),
    Field('status', writable=False, readable=False, default=T("Processing...")),
    Field('language', 'list:string', requires=IS_IN_SET(languages), default='English'),
    Field('price', 'double', default=0.0, comment='$USD'),
    Field('length', 'double', writable=False, readable=False),
    Field('play_count', 'integer', readable=False, writable=False, default=0),
    Field('release_date', 'datetime', comment=T('Select a date to release this recording in the future. UTC(GMT) timezone.')),
    Field('email', requires = IS_EMPTY_OR(IS_EMAIL(error_message=T('Invalid email!'))), comment=T('Email to be sent to (the release notification)')),
    auth.signature,
    format='%(title)s'
)
Sounds.mime_type = Field.Virtual(lambda row: 'audio/mpeg') #'audio/ogg' if row.sounds.file.rsplit('.', 1)[-1] == 'ogg' else 'audio/mpeg')
Sounds.username = Field.Virtual(get_username)
Sounds.owner_email = Field.Virtual(get_email)
Sounds.download_url = Field.Virtual(get_download_url)
Sounds.delete_url = Field.Virtual(get_delete_url)
Sounds.is_active.default = False

a0,a1 = request.args(0), request.args(1)
active_sounds = Sounds.is_active == True
user_sounds = Sounds.created_by == auth.user_id

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
