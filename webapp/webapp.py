from flask import Flask, request, current_app, Blueprint
import requests

admin = Blueprint('admin', __name__, url_prefix='/admin')


def create_app(sd_instance):
    app = Flask(__name__)
    app.config['sd'] = sd_instance
    return app


@admin.route("/oauthcallback")
def oauth_callback():
    sd = current_app.config['sd']
    data = {'client_id': sd.config.slackapp_id,
            'client_secret': sd.config.slackapp_secret, 'code': request.args.get('code')}
    response = requests.post('https://slack.com/api/oauth.access', params=data)
    team = sd.config.add_team(response_dict=response.json())
    sd.monitor_new_slack(team)

    return "Authorization granted!"

