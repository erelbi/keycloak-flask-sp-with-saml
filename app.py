from urllib import request
from flask import Flask, url_for,redirect
from flask_saml2.sp import ServiceProvider
from flask_saml2.utils import certificate_from_file, private_key_from_file
#override
class KeycloakServiceProvider(ServiceProvider):
    def get_logout_return_url(self):
        return url_for('index', _external=True)

    def get_default_login_return_url(self):
        return url_for('index', _external=True)

sp = KeycloakServiceProvider()
app = Flask(__name__)
app.debug = True
app.secret_key = 'not a secret'
app.config['SERVER_NAME'] = '10.242.105.69:5002'
app.config['SAML2_SP'] = {
      'certificate': certificate_from_file('idp_cert.pem'),
    'private_key': private_key_from_file('sp_key.pem'),
}
# Kimlik denetmeleme sağlayıcı
app.config['SAML2_IDENTITY_PROVIDERS'] = [
    {
        'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',
        'OPTIONS': {
            'display_name': 'KeyCloak',
            'entity_id': 'http://10.242.105.240:8080/auth/realms/test',
            'sso_url': 'http://10.242.105.240:8080/auth/realms/test/protocol/saml',
            'slo_url': 'http://10.242.105.240:8080/auth/realms/test/protocol/saml',
            'certificate': certificate_from_file('idp_cert.pem')
        },
    },
]

# AnaSayfa
@app.route('/')
def index():
    if sp.is_user_logged_in():
        auth_data = sp.get_auth_data_in_session()

        message = f'''
        <p>Giriş Yaptınız! Kullanıcı İsmi: <strong>{auth_data.nameid}</strong>
        '''
        logout_url = url_for('flask_saml2_sp.logout')
        logout = f'<form action="{logout_url}" method="POST"><input type="submit" value="Log out"></form>'

        return message +  logout
    else:
        message = '<p>Sisteme Giriş Yapın.</p>'

        login_url = url_for('flask_saml2_sp.login')
        link = f'<p><a href="{login_url}">Giriş</a></p>'

        return message + link

# Çıkış
@app.route('/saml/logout/',methods =['POST'])
def logout():
            sp.logout()
            return redirect(url_for('index'))


# Yönlendir
app.register_blueprint(sp.create_blueprint(), url_prefix='/saml')

# Start
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002)