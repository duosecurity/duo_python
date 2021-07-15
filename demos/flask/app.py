
import os
import sys
import argparse
import flask
import duo_universal

app = flask.Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/", methods=['GET'])
def do_GET():
    # Get the username from the 'user' query argument.  In real life,
    # this will usually be done with framework-appropriate authentication.
    # The local username will be used as the Duo username as well.
    username = flask.request.args.get('user')
    if username is None:
        return 'user query parameter is required', 400

    try:
        app.duo_client.health_check()
    except duo_universal.DuoException:
        return 'Duo health check failed. Logged in without 2FA as %s.' % username
        # alternatively: return 'Duo health check failed, denying login.'

    state = app.duo_client.generate_state()
    prompt_uri = app.duo_client.create_auth_url(username, state)

    flask.session['state'] = state
    flask.session['username'] = username

    return flask.redirect(prompt_uri)

@app.route("/duo-callback", methods=['GET'])
def do_duo_callback():
    state = flask.session['state']
    username = flask.session['username']

    if (state is None) or (username is None) or (state != flask.request.args.get('state')):
        return 'Invalid state or username'

    duo_code = flask.request.args.get('duo_code')
    if duo_code is None:
        return 'duo_code post parameter is required', 400

    try:
        app.duo_client.exchange_authorization_code_for_2fa_result(duo_code, username)
    except duo_universal.DuoException:
        return 'Did not authenticate with Duo.'.encode('utf-8')

    return ('Authenticated with Duo as %s.' % username).encode('utf-8')


def main(client_id, client_secret, host, redirect_uri, port=8080):
    port = int(port)
    app.duo_client = duo_universal.Client(
        client_id=client_id,
        client_secret=client_secret,
        host=host,
        redirect_uri=redirect_uri
    )
    print("Visit the root URL with a 'user' argument, e.g.")
    print("'http://localhost:%d/?user=myname'." % port)
    app.run(host="0.0.0.0", port=8080)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c", "--config",
        help="The config section from duo.conf to use",
        default="duo",
        metavar='')

    return parser.parse_args()


if __name__ == '__main__':
    import six.moves.configparser as ConfigParser

    filename = "duo.conf"
    directory = os.path.join("demos", "flask")
    path = os.path.join(directory, filename)

    config = ConfigParser.ConfigParser()
    if os.path.exists(filename):
        config.read(filename)
    else:
        print(
            "Couldn't find {}, are you sure you're in {}?".format(
                filename, directory))
        sys.exit(1)

    args = parse_args()
    main(**dict(config.items(args.config)))
