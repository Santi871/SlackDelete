import configparser


class SDConfig:

    def __init__(self, config_name):

        self.config = configparser.ConfigParser()
        self.config_name = config_name
        self.slackapp_id = None
        self.slackapp_secret = None
        self.slackapp_cmds_secret = None
        self.whitelist = None
        self._update()
        self.teams = self._get_slack_teams()

    def _update(self):
        self.config.read(self.config_name)
        self.slackapp_id = self.config['credentials']['slackapp_id']
        self.slackapp_secret = self.config['credentials']['slackapp_secret']
        self.slackapp_cmds_secret = self.config['credentials']['slackapp_cmds_secret']

    def _get_slack_teams(self):
        teams = list()
        for section in self.config.sections():
            if section != 'credentials':
                team = SlackTeam(section, team_id=self.config[section]['team_id'],
                                 access_token=self.config[section]['access_token'],
                                 bot_access_token=self.config[section]['bot_access_token'],
                                 whitelist=self.config[section]['whitelist'].split(','))
                teams.append(team)
        return teams

    def whitelist_user(self, team, user):
        whitelist = self.config[team]['whitelist'].split(',')
        whitelist.remove("None")

        if user not in whitelist:
            whitelist.append(user)
            self.config[team]['whitelist'] = ','.join(whitelist)
            with open(self.config_name, 'w') as configfile:
                self.config.write(configfile)

    def unwhitelist_user(self, team, user):
        whitelist = self.config[team]['whitelist'].split(',')
        if user in whitelist:
            whitelist.remove(user)
            whitelist = ','.join(whitelist)

            if whitelist != "":
                self.config[team]['whitelist'] = whitelist
            else:
                self.config[team]['whitelist'] = "None"

            with open(self.config_name, 'w') as configfile:
                self.config.write(configfile)

    def add_team(self, response_dict):

        if not response_dict['ok']:
            return False

        team_name = response_dict['team_name']
        team_id = response_dict['team_id']
        access_token = response_dict['access_token']
        bot_access_token = response_dict['bot']['bot_access_token']

        try:
            self.config.add_section(team_name)
            self.config[team_name]['whitelist'] = "None"
        except configparser.DuplicateSectionError:
            pass
        finally:
            self.config[team_name]["team_id"] = team_id
            self.config[team_name]['access_token'] = access_token
            self.config[team_name]['bot_access_token'] = bot_access_token
            with open(self.config_name, 'w') as configfile:
                self.config.write(configfile)
            team = SlackTeam(team_name, team_id, access_token, bot_access_token, None)
            self.teams.append(team)

            return team


class SlackTeam:

    def __init__(self, team_name, team_id, access_token, bot_access_token, whitelist):
        self.team_name = team_name
        self.team_id = team_id
        self.access_token = access_token
        self.bot_access_token = bot_access_token
        self.whitelist = whitelist

