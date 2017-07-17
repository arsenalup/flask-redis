#-*- coding: utf-8 -*-
import datetime
import flask
import redis
from flask import Flask, render_template


app = flask.Flask(__name__)
app.secret_key = 'asdf'
r = redis.StrictRedis(host='localhost', port=6379, db=1)


def event_stream():
    pubsub = r.pubsub()
    pubsub.subscribe('chat')
    for message in pubsub.listen():
        print(message)
        yield u'data: %s\n\n' %(message['data'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        #保存消息至session
        flask.session['user'] = flask.request.form['user']
        return flask.redirect('/')
    return '<form action = "" method="post">user: <input name = "user">'


#接受JS消息
@app.route('/post', methods=['POST'])
def post():
    message = flask.request.form['message']
    user = flask.session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    #发布消息到chat
    r.publish('chat', u'[%s] %s: %s' %(now.isoformat(), user, message))
    return flask.Response(status = 204)


#事件流接口
@app.route('/stream')
def stream():
    #返回类型'test/event=stream',确认SSE事件流
    return flask.Response(event_stream(), mimetype = "text/event-stream")


@app.route('/')
def home():
    #强制登陆
    if 'user' not in flask.session:
        return flask.redirect('/login')
    user = flask.session['user']
    return render_template('index.html', user=user)



if __name__ == '__main__':
    app.run(debug=True, threaded=True)