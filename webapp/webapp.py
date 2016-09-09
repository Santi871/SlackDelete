from flask import Flask, request
import requests
from slackdelete.slackdelete import SlackRequest, SlackDelete

app = Flask(__name__)
sd = SlackDelete('config.ini')
sd.monitor_all_slacks()


@app.route("/oauthcallback")
def oauth_callback():
    data = {'client_id': sd.config.slackapp_id,
            'client_secret': sd.config.slackapp_secret, 'code': request.args.get('code')}
    response = requests.post('https://slack.com/api/oauth.access', params=data)
    team = sd.config.add_team(response_dict=response.json())
    sd.monitor_new_slack(team)

    return "Authorization granted!"


@app.route('/slack/commands', methods=['POST'])
def command():
    slack_request = SlackRequest(request, sd.config.slackapp_cmds_secret)
    response = 'Invalid request token'
    if slack_request.is_valid:
        if slack_request.command == '/sdwhitelist':
            response = sd.whitelist_user(slack_request.team_domain, slack_request.text.split()[0])
        elif slack_request.command == '/sdunwhitelist':
            response = sd.unwhitelist_user(slack_request.team_domain, slack_request.text.split()[0])

    return response

