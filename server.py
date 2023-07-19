from quart import Quart, render_template, redirect, jsonify, request, Response
from quart_cors import cors
import asqlite
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



app = cors(Quart(__name__), allow_origin='*')
app.config['SECRET_KEY'] = "8339585083"
app.config['DISCORD_CLIENT_ID'] = OauthInformation.CLIENTID
app.config['DISCORD_CLIENT_SECRET'] = OauthInformation.CLIENTSECRET
app.config['DISCORD_REDIRECT_URI']  = OauthInformation.REDIRECT_URI
discord = quart_discord.DiscordOAuth2Session(app)

@app.route('/')
async def logindiscord():
    return await render_template('index.html')


@app.route('/login') # voor het authorize met een code (wordt later getrade met een access token van discord)
async def loginaccesscode():
    return await discord.create_session()


@app.route('/discord-callback')
async def discordcallback():
    try:
        await discord.callback()
        return redirect('/somtodayverification')
    except:
        return redirect('/login')


@app.route('/somtodayverification')
@quart_discord.requires_authorization
async def verifysomtoday():
    async with asqlite.connect('./information.db') as connection:
        async with connection.cursor() as cursor:
            user = await discord.fetch_user()

            await cursor.execute('''
            INSERT INTO somtodayqueue VALUES(
            ?,
            ?
            );
            ''', (user.id, False))
            await connection.commit()
            return await render_template('pending.html', user=user)


@app.route('/user-has-been-linked', methods=['GET'])
async def userhasbeenlinked():
    async with asqlite.connect('./information.db') as connection:
        async with connection.cursor() as cursor:
            if request.args.get('discordID', 'n').isnumeric() == False:
                return Response({'error': 'discordID parameter is missing'}, status=400, mimetype='application/json')

            await cursor.execute('''
            SELECT linked FROM somtodayqueue WHERE discordID=?;
            ''', (request.args.get('discordID'),))
            fetch  = await cursor.fetchone()
            if fetch != None and len(fetch) == 1 and fetch[0] == 1:
                response = jsonify({'linked': True})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET')
                return response
                    
            else:
                response = jsonify({'linked': False})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET')
                return response


if __name__ == '__main__':
    app.run(port=3000, debug=True)
