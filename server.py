import quart_discord.models
from quart import Quart, render_template, redirect
from dotenv import load_dotenv
import quart_discord
from os import getenv

load_dotenv()


class OauthInformation:
    '''
    Een class die bestaat uit meta informatie die je kan vinden in discord.com/developers
    '''
    CLIENTID: str = str(getenv('CLIENT_ID', ''))
    CLIENTSECRET: str = getenv('CLIENT_SECRET')
    REDIRECT_URI: str = getenv('REDIRECT_URI')
    SCOPES: str = getenv('SCOPE')
    DISCORD_LOGIN_URL: str = getenv('DISCORD_LOGIN_URL')
    DISCORD_TOKEN_URL: str = 'https://discord.com/api/oauth2/token'
    DISCORD_API_URL: str = 'https://discord.com/api'

    @staticmethod
    def exchange_code(code: str) -> str:
        '''
        :param code: De code geparst via de url
        :return: de access token
        '''
        payload = {
            'client_id': OauthInformation.CLIENTID,
            'client_secret': OauthInformation.CLIENTSECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': OauthInformation.REDIRECT_URI,
            'scope': OauthInformation.SCOPES
        }


app = Quart(__name__)
app.config['SECRET_KEY'] = "8339585083"
app.config['DISCORD_CLIENT_ID'] = OauthInformation.CLIENTID
app.config['DISCORD_CLIENT_SECRET'] = OauthInformation.CLIENTSECRET
app.config['DISCORD_REDIRECT_URI']  = OauthInformation.REDIRECT_URI
discord = quart_discord.DiscordOAuth2Session(app)


@app.route('/')
async def logindiscord():
    return await render_template('index.html')


@app.route('/login/') # voor het authorize met een code (wordt later getrade met een access token van discord)
async def loginaccesscode():
    return await discord.create_session()


@app.route('/discord-callback')
async def discordcallback():
    try:
        await discord.callback()
        return redirect('/somtoday/')
    except:
        return redirect('/login/')


@app.route('/somtoday/')
async def somtodayssocheck():
    somtoday_auth_url = "https://somtoday.nl/oauth2/authorize"
    redirect_uri = "somtodayleerling://callback"

    client_id = "D50E0C06-32D1-4B41-A137-A9A850C892C2"
    response_type = "code"
    prompt = "login"
    scope = "openid"
    code_challenge = "tCqjy6FPb1kdOfvSa43D8a7j8FLDmKFCAz8EdRGdtQA"
    code_challenge_method = "S256"
    tenant_uuid = "18d45fa7-16e4-4334-a6a6-0b9633a2798b"
    oidc_iss = "https://studio01.school-studios.wis.nl/"

    auth_url = f"{somtoday_auth_url}?redirect_uri={redirect_uri}&client_id={client_id}&response_type={response_type}&prompt={prompt}&scope={scope}&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}&tenant_uuid={tenant_uuid}&oidc_iss={oidc_iss}"

    return redirect(auth_url)


if __name__ == '__main__':
    app.run(port=3000, debug=True)
