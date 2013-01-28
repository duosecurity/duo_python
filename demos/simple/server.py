from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import urlparse
import cgi

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
            f = open(path, 'rb')
        except IOError:
            raise
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def require_query(self, name):
        """
        Return the query argument value for given argument name,
        or raise ValueError.
        """
        path = urlparse.urlparse(self.path)
        try:
            return urlparse.parse_qs(path.query)[name][0]
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
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],})
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
            self.error('user query parameter is required')
            return
        self.send_response(200)
        self.end_headers()

        # Pass in "enroll=1" parameter to trigger enroll only mode
        sign_function = duo_web.sign_request
        try:
            enroll = self.require_query('enroll')
            sign_function = duo_web.sign_enroll_request
        except ValueError:
            pass

        sig_request = sign_function(
            self.server.ikey, self.server.skey, self.server.akey, username)
        self.wfile.write(
            "<script src='/Duo-Web-v1.bundled.min.js'></script>"
            "<script>"
            "Duo.init({'host':'%(host)s', 'sig_request':'%(sig_request)s'});"
            "</script>"
            "<iframe height='100%%' width='100%%' id='duo_iframe' />"
            % {'host':self.server.host, 'sig_request':sig_request})
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
            user = duo_web.verify_enroll_response(self.server.ikey,
                self.server.skey, self.server.akey, sig_response)
            if user is None:
                self.wfile.write('Did not authenticate with Duo.')
            else:
                self.wfile.write('Enrolled with Duo as %s.' % user)
        else:
            self.wfile.write('Authenticated with Duo as %s.' % user)
        

def main(ikey, skey, akey, host, port=8080):
    server = HTTPServer(('', port), RequestHandler)
    server.ikey = ikey
    server.skey = skey
    server.akey = akey
    server.host = host
    print "Visit the root URL with a 'user' argument, e.g."
    print "'http://localhost:%d/?user=myname'." %  port
    server.serve_forever()
                                                        
if __name__ == '__main__':
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('duo.conf')
    main(**dict(config.items('duo')))
