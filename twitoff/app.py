"""Main application and routing logic for TwitOff."""
from flask import Flask, render_template, request
from .models import *
from .toy_data import toy_data
from jinja2 import Environment, PackageLoader, select_autoescape
from decouple import config
from .twitter import add_twitter_user, get_tweets, add_or_update_user
# from console_log import ConsoleLog

# console = logging.getLogger('console')
# console.setLevel(logging.DEBUG)


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ENV'] = config('FLASK_ENV')  # TODO change before deploying
    DB.init_app(app)
    # env = Environment(
    #     loader=PackageLoader('twitoff', 'templates'),
    #     autoescape=select_autoescape(['html', 'xml'])
    # )

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Users', users=users)

    @app.route('/repopulate')
    def repopulate():
        toy_data(DB)
        return render_template('base.html')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset', users=[])

    @app.route('/user/<username>', methods=['GET'])
    def show(username):
        (text, user) = get_tweets(username)
        if user is None:
            return text
        return render_template('show.html', title='Tweets', user=user)

    @app.route('/user/<username>', methods=['POST'])
    def add_user(username):
        (text, user) = add_twitter_user(username)
        if user is None:
            return text
        return render_template('show.html', title='Tweets', user=user)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = 'User {} successfully added!'.format(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)


    return app
