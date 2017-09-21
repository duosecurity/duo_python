from six.moves.BaseHTTPServer import HTTPServer
from six.moves.SimpleHTTPServer import SimpleHTTPRequestHandler
from six.moves.urllib.parse import urlparse, parse_qs
import cgi
import os
import sys

import duo_web


class RequestHandler(SimpleHTTPRequestHandler):

    def error(self, msg):
        """
        Write an error 400.
        """
        self.send_response(400, msg)
        self.end_headers()
        self.wfile.write(msg)

    def serve_file(self):
        """
        If a file exists corresponding to the request's path, serve it.
        Otherwise, raise IOError.
        """
        path = self.translate_path(self.path)
        try:
            open(path, 'rb')
        except IOError:
            raise
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def require_query(self, name):
        """
        Return the query argument value for given argument name,
        or raise ValueError.
        """
        path = urlparse(self.path)
        try:
            return parse_qs(path.query)[name][0]
        except:
            raise ValueError

    def require_post(self, name):
        """
        Return the POST argument value for given argument name,
        or raise ValueError.
        """
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type']})
        try:
            return form[name].value
        except:
            raise ValueError

    def do_GET(self):
        try:
            self.serve_file()
        except IOError:
            pass
        else:
            return                      # we served a file from the FS

        # Get the username from the 'user' query argument.  In real life,
        # this will usually be done with framework-appropriate authentication.
        # The local username will be used as the Duo username as well.
        try:
            username = self.require_query('user')
        except ValueError:
            self.error(b'user query parameter is required')
            return
        self.send_response(200)
        self.end_headers()

        # Pass in "enroll=1" parameter to trigger enroll only mode
        sign_function = duo_web.sign_request
        try:
            self.require_query('enroll')
            sign_function = duo_web.sign_enroll_request
        except ValueError:
            pass

        sig_request = sign_function(
            self.server.ikey, self.server.skey, self.server.akey, username)
        out = """
            <!DOCTYPE html>
            <html>
              <head>
                <title>Duo Authentication Prompt</title>
                <meta name='viewport' content='width=device-width, initial-scale=1'>
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <link rel="stylesheet" type="text/css" href="Duo-Frame.css">
              </head>
              <body>
                <h1>Duo Authentication Prompt</h1>
                <script src='/Duo-Web-v2.js'></script>
                <iframe id="duo_iframe"
                        title="Two-Factor Authentication"
                        frameborder="0"
                        data-host="%(host)s"
                        data-sig-request="%(sig_request)s"
                        >
                </iframe>
              </body>
            </html> """ % {
                'host': self.server.host,
                'sig_request': sig_request}

        self.wfile.write(out.encode('utf-8'))

        return

    def do_POST(self):
        try:
            sig_response = self.require_post('sig_response')
        except ValueError:
            self.error('sig_response post parameter is required')
            return
        user = duo_web.verify_response(
            self.server.ikey, self.server.skey, self.server.akey, sig_response)

        self.send_response(200)
        self.end_headers()

        if user is None:
            # See if it was a response to an ENROLL_REQUEST
            user = duo_web.verify_enroll_response(
                self.server.ikey, self.server.skey,
                self.server.akey, sig_response)
            if user is None:
                self.wfile.write(
                    ('Did not authenticate with Duo.'.encode('utf-8')))
            else:
                self.wfile.write(
                    ('Enrolled with Duo as %s.' % user).encode('utf-8'))
        else:
            self.wfile.write(
                ('Authenticated with Duo as %s.' % user).encode('utf-8'))


def main(ikey, skey, akey, host, port=8080):
    port = int(port)
    server = HTTPServer(('', port), RequestHandler)
    server.ikey = ikey
    server.skey = skey
    server.akey = akey
    server.host = host
    print("Visit the root URL with a 'user' argument, e.g.")
    print("'http://localhost:%d/?user=myname'." % port)
    server.serve_forever()

if __name__ == '__main__':
    import six.moves.configparser as ConfigParser

    filename = "duo.conf"
    directory = os.path.join("demos", "simple")
    path = os.path.join(directory, filename)

    config = ConfigParser.ConfigParser()
    if os.path.exists(filename):
        config.read(filename)
    else:
        print(
            "Couldn't find {}, are you sure you're in {}?".format(
                filename, directory))
        sys.exit(1)

    main(**dict(config.items('duo')))
