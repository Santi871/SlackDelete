from webapp.webapp import app

if __name__ == "__main__":
    context = ('santihub.crt', 'santihub.key')
    app.run(host='0.0.0.0', ssl_context=context, port=5011, threaded=True)
