#!/usr/bin/python

# Author: Gopal Yalla
# Date: 3/17/2015
#
# Geolocation service top level program. Run it like this:
#   ./geolocation.py <host> <port>
# or like this:
#   python geolocation.py <host> <port>
# where <host> is the DNS name of the host that will be the central coordinator,
# and <port> is the port on which the central coordinator will serve HTTP
# requests from users.
#
# example: ./geolocate ec2-18-218-156-22.us-east-2.compute.amazonaws.com 2000
import sys            # for sys.argv
import socket 

# Get the central_host name and port number from the command line
central_host = sys.argv[1]
central_port = int(sys.argv[2])


#Use urlparse to decode url and fetch data
def fetch_url(url):
    try:
        from urllib import urlparse
    except:
        from urlparse import urlparse
    
    URL = urlparse(url) 

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    try:
        client_socket.connect((URL.netloc.split(':')[0],URL.port))
    except Exception as e: 
        #print 'Default port 80'
        client_socket.connect((URL.netloc.split(':')[0],80))

    rqst  = 'GET ' + URL.path + ' HTTP/1.1\r\n'
    rqst += 'Host: ' + URL.netloc.split(':')[0]+'\r\n\r\n'
    client_socket.send(rqst)
    rsp = client_socket.recv(2048)
    
    return rsp.splitlines()[-1]

# Figure out our own host name. 
dns_name = fetch_url('http://169.254.169.254/latest/meta-data/public-hostname')
print "DNS NAME=",dns_name

# Figure out our own ec2 region
region = fetch_url('http://169.254.169.254/latest/meta-data/placement/availability-zone/')
print "Region=",region

##IF WE ARE THE CENTRAL SERVER
if str(dns_name) == str(central_host):
    print 'THIS IS CENTRAL'
    from central import *
    run_central_coordinator(central_host, central_port)
##IF WE ARE A PINGER SERVER
else:
    print 'THIS IS PINGER'
    from pinger import *
    run_pinger_server(dns_name, region,9000,central_host, central_port)

