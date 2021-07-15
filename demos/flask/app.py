
import os
import sys
import argparse
import flask
import duo_universal

app = flask.Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.urandom(32)

@app.route("/", methods=['GET'])
def do_GET():
    # Get the username from the 'user' query argument.  In real life,
    # this will usually be done with framework-appropriate authentication.
    # The local username will be used as the Duo username as well.
    username = flask.request.args.get('user')
    if username is None:
        return 'user query parameter is required', 400

    sig_request = duo_web.sign_request(app.ikey, app.skey, app.akey, username)
    return flask.render_template('index.html', host=app.host, sig_request=sig_request)

@app.route("/", methods=['POST'])
def do_POST():
    sig_response = flask.request.form.get('sig_response')
    if sig_response is None:
        return 'sig_response post parameter is required', 400
    user = duo_web.verify_response(
        app.ikey, app.skey, app.akey, sig_response)

    if user is None:
        return 'Did not authenticate with Duo.'.encode('utf-8')

    return ('Authenticated with Duo as %s.' % user).encode('utf-8')


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
