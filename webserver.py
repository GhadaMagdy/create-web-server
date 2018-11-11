from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from urllib.parse import parse_qs
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
             if self.path.endswith("/restaurants"):
                restaurants=session.query(Restaurant).all()
                output = ""
                # Objective 3 Step 1 - Create a Link to create a new menu item
                output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    # Objective 2 -- Add Edit and Delete Links
                    output += "<a href ='/restaurants/%s/edit' >Edit </a> " % restaurant.id
                    output += "</br>"
                    output += "<a href ='/restaurants/%s/delete' >Delete </a> " % restaurant.id
                    output += "</br></br></br>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

             if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output.encode())
                return 
                
             if self.path.endswith("/edit"):

                 restId=self.path.split("/")[2]
                 Erestaurant=session.query(Restaurant).filter_by(id = restId).one()
                 if Erestaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output=""
                    output+="<html><body>"
                    output+="<h1>%s</h1>" % Erestaurant.name
                    output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/%s/edit'>" % restId
                    output += "<input name = 'editRestaurant' type = 'text' placeholder = '%s' > " %Erestaurant.name
                    output += "<input type='submit' value='Rename'>"
                    output += "</form></body></html>"
                    self.wfile.write(output.encode())
                    return 

             if self.path.endswith("/delete"):
                 restId=self.path.split("/")[2]
                 Erestaurant=session.query(Restaurant).filter_by(id = restId).one()
                 if Erestaurant:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        output=""
                        output+="<html><body>"
                        output+="<h1>Do you want to delete %s</h1>" % Erestaurant.name
                        output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restId
                        output += "<input type='submit' value='delete'>"
                        output += "</form></body></html>"
                        self.wfile.write(output.encode())
                        return
    
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                # boundary data needs to be encoded in a binary format
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name = fields.get('newRestaurantName')
                    
                    newRestaurant = Restaurant(name = format(name[0].decode())) 
                    session.add(newRestaurant)
                    session.commit() 

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                restId=self.path.split("/")[2]
                Erestaurant=session.query(Restaurant).filter_by(id = restId).one()
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                # boundary data needs to be encoded in a binary format
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name = fields.get('editRestaurant')
                    if Erestaurant:
                        Erestaurant.name=format(name[0].decode())
                        session.add(Erestaurant)
                        session.commit() 

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
            
            if self.path.endswith("/delete"):
                restId=self.path.split("/")[2]
                Erestaurant=session.query(Restaurant).filter_by(id = restId).one()
                if Erestaurant:
                    session.delete(Erestaurant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()


        except:
            print ('error')




def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print ("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()