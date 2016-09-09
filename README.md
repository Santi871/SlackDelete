# SlackDelete
SlackDelete deletes messages from channels if they weren't posted by a list of whitelisted users or team admins.


Useful for announcements-only channels and the like.

[![alt text](https://platform.slack-edge.com/img/add_to_slack.png)](https://slack.com/oauth/authorize?scope=commands,bot,channels:read,chat:write:bot&client_id=19729314800.77855559317)

## Usage

1. Add to Slack with the button above.
2. On the channels you want SlackDelete to be active, type `/invite @slackdelete`.
3. Optionally, use `/sdwhitelist [user]` and `/sdunwhitelist [user]` to manage whitelisted users. Use `/sdwhitelisted` to
view whitelisted users.

Note: Only team admins may add or remove whitelisted users.

Note2: Whitelisted users are per team, affecting all channels in which SlackDelete is active.

To remove SlackDelete from a channel, use `/remove @slackdelete` while on the channel you want to kick it from.