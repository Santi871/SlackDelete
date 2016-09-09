from slackdelete.slackdelete import SlackDelete
from webapp.webapp import create_app

if __name__ == "__main__":
    sd = SlackDelete('config.ini')
    sd.monitor_all_slacks()
    app = create_app(sd)
    app.run(host='0.0.0.0', port=5011)
