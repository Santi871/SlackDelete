import json
from threading import Thread

import requests
from slacksocket import SlackSocket

from slackdelete.config import SDConfig


class SlackDelete:

    def __init__(self, config_name):
        self.config = SDConfig(config_name)

    def monitor_all_slacks(self):
        for team in self.config.teams:
            s = SlackSocket(team.bot_access_token, translate=False, event_filters=['message'])
            t = Thread(name="Slackmonitor, team: " + team.team_name, target=monitor_slack_events,
                       args=[s, team.access_token, team.whitelist])
            t.start()

    @staticmethod
    def monitor_new_slack(team):
        s = SlackSocket(team.bot_access_token, translate=False, event_filters=['message'])
        t = Thread(name="Slackmonitor, team: " + team.team_name,
                   target=monitor_slack_events, args=[s, team.access_token, team.whitelist])
        t.start()


def monitor_slack_events(s, access_token, whitelist):
    for event in s.events():
        event_dict = json.loads(event.json)
        event_subtype = event_dict.get('subtype', None)
        if event_subtype is not None:
            continue

        user = event_dict['user']
        message_ts = event_dict['ts']
        channel = event_dict['channel']
        params = {'token': access_token, 'user': user}
        response = requests.get("https://slack.com/api/users.info", params=params).json()
        is_admin = response['user']['is_admin']
        user = response['user']['name']

        if is_admin and user not in whitelist:
            params = {'token': access_token, 'channel': channel, 'ts': message_ts}
            response = requests.get("https://slack.com/api/chat.delete", params=params)
            if not response.json()['ok']:
                break
