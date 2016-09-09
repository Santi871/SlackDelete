from slackdelete.slackdelete import SlackDelete
from webapp.webapp import create_app

if __name__ == "__main__":
    sd = SlackDelete('config.ini')
    sd.monitor_all_slacks()
    app = create_app(sd)
    context = ('santihub.crt', 'santihub.key')
    app.run(host='0.0.0.0', ssl_context=context, port=5011, threaded=True)
