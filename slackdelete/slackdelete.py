import json
from threading import Thread
import requests
from slacksocket import SlackSocket
from slackdelete.config import SDConfig


class SlackDelete:

    def __init__(self, config_name):
        self.config = SDConfig(config_name)
        self.whitelists = dict()
        self.access_tokens = dict()

        for team in self.config.teams:
            self.whitelists[team.team_name] = team.whitelist
            self.access_tokens[team.team_name] = team.access_token

    def monitor_all_slacks(self):
        for team in self.config.teams:
            s = SlackSocket(team.bot_access_token, translate=False, event_filters=['message'])
            t = Thread(name="Slackmonitor, team: " + team.team_name, target=self.monitor_slack_events,
                       args=[s, team.access_token, team.team_name])
            t.start()

    def monitor_new_slack(self, team):
        s = SlackSocket(team.bot_access_token, translate=False, event_filters=['message'])
        t = Thread(name="Slackmonitor, team: " + team.team_name,
                   target=self.monitor_slack_events, args=[s, team.access_token, team.team_name])
        t.start()

    def whitelist_user(self, team, user, author):
        retval = "Whitelisted user."
        params = {'token': self.access_tokens[team], 'user': author}
        response = requests.get("https://slack.com/api/users.info", params=params).json()
        is_admin = response['user']['is_admin']

        if user not in self.whitelists[team] and is_admin:
            self.whitelists[team].append(user)
            self.config.whitelist_user(team, user)
        elif user in self.whitelists[team]:
            retval = "Failed to whitelist user: user already whitelisted."
        elif not is_admin:
            retval = "Failed to whitelist user: you must be an admin to run this command."

        return retval

    def unwhitelist_user(self, team, user, author):
        retval = "Unwhitelisted user."
        params = {'token': self.access_tokens[team], 'user': author}
        response = requests.get("https://slack.com/api/users.info", params=params).json()
        is_admin = response['user']['is_admin']

        if user in self.whitelists[team]:
            self.whitelists[team].remove(user)
            self.config.unwhitelist_user(team, user)
        elif user not in self.whitelists[team]:
            retval = "Failed to unwhitelist user: user not in whitelist."
        elif not is_admin:
            retval = "Failed to unwhitelist user: you must be an admin to run this command."

        return retval

    def show_whitelist(self, team):
        if self.whitelists[team] == ["None"]:
            return "Whitelist is empty."

        retval = "Showing whitelist:\n"

        for user in self.whitelists[team]:
            retval += "-" + user

        return retval

    def monitor_slack_events(self, s, access_token, team_name):
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

            if not is_admin and user not in self.whitelists[team_name]:
                params = {'token': access_token, 'channel': channel, 'ts': message_ts}
                response = requests.get("https://slack.com/api/chat.delete", params=params)
                if not response.json()['ok']:
                    break


class SlackRequest:

    """Parses HTTP request from Slack"""

    def __init__(self, request, secret):

        self.form = request.form
        self.request_type = "command"
        self.response = None
        self.command = None
        self.actions = None
        self.callback_id = None
        self.is_valid = False

        if 'payload' in self.form:
            self.request_type = "button"
            self.form = json.loads(dict(self.form)['payload'][0])
            self.user = self.form['user']['name']
            self.user_id = self.form['user']['id']
            self.team_domain = self.form['team']['domain']
            self.team_id = self.form['team']['id']
            self.callback_id = self.form['callback_id']
            self.actions = self.form['actions']
            self.message_ts = self.form['message_ts']
            self.original_message = self.form['original_message']
        else:
            self.user = self.form['user_name']
            self.user_id = self.form['user_id']
            self.team_domain = self.form['team_domain']
            self.team_id = self.form['team_id']
            self.command = self.form['command']
            self.text = self.form['text']
            self.channel_name = self.form['channel_name']

        self.response_url = self.form['response_url']
        self.token = self.form['token']

        if self.token == secret:
            self.is_valid = True

    def delayed_response(self, response):

        headers = {"content-type": "plain/text"}

        slack_response = requests.post(self.response_url, data=response, headers=headers)

        return slack_response
