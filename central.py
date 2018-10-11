#!/usr/bin/python
#############################################################
# Gopal Yalla
# 3/20/2015
# Purpose: Implementation of the central server for geolocation service
#############################################################
import socket
import sys
import os
import time
import threading
import urllib


#############################
# Decode_Region(region) 
# 
# Determines the location and lat/log coordinates 
# given a pinger server region. Need to update as amazon
# adds more regions.
############################
def Decode_Region(region):
    
    if region == 'sa-east-1':
        loc = 'Sao Paulo' 
        corr = [-23.34,-46.38]
    elif region == 'eu-central-1':
        loc = 'Frankfurt' 
        corr = [50.1167,8.6833]
    elif region == 'eu-west-1':
        loc = 'Ireland'
        corr = [53,-8]; 
    elif region == 'us-east-1':
        loc = 'N. Virginia'
        corr = [38.13, -78.45]
    elif region == 'us-west-1':
        loc = 'N. California'
        corr = [41.48,-120.53]
    elif region == 'us-west-2':
        loc = 'Oregon'
        corr = [46.15,-123.88]
    elif region == 'ap-southeast-1':
        loc = 'Singapore' 
        corr = [1.37, 103.8]
    elif region == 'ap-northeast-1': 
        loc = 'Tokyo' 
        corr = [35.41,139.42]
    elif region == 'ap-southeast-2':
        loc = 'Sydney'
        corr = [-33.86,151.2] 
    else :
        loc = 'Unknown'
        corr = [-1,-1] 

    return (loc,corr); 


###############################
# Geolocate(url)
#
# Main Geolocation Function. It sends a rqst to each pinger and recieves 
# their response, and check if some pingers have closed.  
###############################
def Geolocate(url):
    global pinger_list

    min_time = 10 #Longer than timeout time 
    closed_pingers = []; 
    print pinger_list
    msg = 'Error: No pingers active'
    client_socket = []
    
    #Send each pinger rqst for target
    for i in range(0,len(pinger_list)/2):
        client_socket.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        
        client_socket[i].settimeout(7) #in case machine was killed
        try: 
            client_socket[i].connect((pinger_list[i*2],9000))
            print 'Connected to Pinger' + str(i)
            rqst = 'AWS ' + url + '\r\n\r\n'
            client_socket[i].send(rqst)
        except Exception as e:
            print e
            print 'AWS Pinger Closed: ' + pinger_list[i*2]
            closed_pingers.append(i)

    #Recieve each rqst from pinger
    for i in range(0,len(pinger_list)/2):
        try: 
            rsp = client_socket[i].recv(2048)
            rsp = rsp.split()
            if len(rsp) == 2:
                msg = aws_parse(rsp)
            elif float(rsp[4]) < min_time:
                min_time = float(rsp[4])
                msg = aws_parse(rsp)
        except Exception as e:
            print e
    #Remove pingers that are closed 
    while len(closed_pingers) != 0:
        indx = closed_pingers.pop()
        del pinger_list[indx*2]
        del pinger_list[indx*2]

    return msg


###################################
# Create_Client_RSP(msg,status,filetype,keep_alive):
#
# Creates response to send back to client machine 
##################################
def Create_Client_RSP(msg,status,filetype,keep_alive):
    if keep_alive:
        connect = 'keep-alive'
    else:
        connect = 'close'

    rsp =  'HTTP/1.1 ' + status + '\r\n'
    rsp += 'Date: ' + time.strftime("%c") + '\r\n'
    rsp += 'Server: AwesomeWebServer (gyalla) \r\n'
    rsp += 'Content-Length: ' + str(len(msg)) + '\r\n'
    rsp += 'Connection: '+ connect + '\r\n' 
    rsp += 'Content-Type: ' + filetype+ ' \r\n\r\n'
    rsp += msg

    return rsp 

##################################
# GetFileType(pwd):
#
# Determines Filetype. This isn't really used but was 
# copied from project 1 
#################################
def GetFileType(pwd):
    fileExt = os.path.splitext(pwd)[1]
    fileExt = fileExt.lower(); 
    
    if fileExt  == '.html':
        return 'text/html'
    if fileExt == '.jpg':
        return 'image/jpeg'
    if fileExt == '.png':
        return 'image/png'
    if fileExt == '.css':
        return 'text/css'
    if fileExt == '.js':
        return  'text/javascript'
    else:
        return 'text/plain'

#########################
#  Main_Page()
#
#  Creates the HTML for the main home page 
########################
def Main_Page():

    msg  = '<html> \n'
    msg += '<head><title>Goopey\'s Geolocation service</title></head>'
    msg += '<body style="background-color:lightblue">'
    msg += '  <h1>Welcome to Goopey\'s Geolocation service</h1>'
    msg += '  <p>There are currently ' + str(len(pinger_list)/2)+ ' active pinger clients:</p>'
    msg += '\n'
    msg += '  <pre>'
    for i in range(0,len(pinger_list)/2):
        msg += pinger_list[i*2] + '   ('+ Decode_Region(pinger_list[i*2+1][:-1])[0]+ ')  \n' 
    msg += '  </pre>'
    msg += '    <form action="/geolocate" method="GET">'
    msg += '      Enter a url:'
    msg += '      <input type="text" name="target" size="80" value="http://www.something.com/index.html">'
    msg += '      <input type="submit">'
    msg += '   </form>'
    msg += '  <img src="http://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap&markers=color:red'
    for i in range(0,len(pinger_list)/2):
        msg += '|'+ str(Decode_Region(pinger_list[i*2+1][:-1])[1][0]) +',' + str(Decode_Region(pinger_list[i*2+1][:-1])[1][1])
    msg += '&zoom=1" />'
    msg += '</body>'
    msg += '</html>'

    return msg

################################
# client_parse(rqst_wrds)
#
# Parse each clients possible rqsts and determines appropriate 
# response. 
##############################
def client_parse(rqst_wrds):
    global pinger_list
    closed_pingers = []; 

    #Case for geolocation 
    if rqst_wrds[1].split('=')[0] == '/geolocate?target':
        msg = Geolocate(urllib.unquote(rqst_wrds[1].split('=')[1]))
        status = '200 OK'
        filetype = 'text/html'
    #Everything Else 
    elif 1:
        #THIS IS NEED IF YOU REFRESH HOME PAGE
        for i in range(0,len(pinger_list)/2):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(7)
            try:
                client_socket.connect((pinger_list[i*2],9000))
                client_socket.sendall('AWS HELLO')
            except Exception as e:
                print e
                closed_pingers.append(i)
            client_socket.close()
        
        while len(closed_pingers) != 0:
            indx = closed_pingers.pop()
            del pinger_list[indx*2]
            del pinger_list[indx*2]

        status  = '200 OK'
        filetype = 'text/html'
        msg = Main_Page(); 

    #Not used, but from project1. I thought just having a default home page
    #made sense. 
    else: 
        pwd = dir_name+rqst_wrds[1]
        if os.path.isdir(pwd):
            pwd += '/index.html'
            if not os.path.isfile(pwd):
                status = '404 NOT FOUND'
            else:
                status = '200 OK'
                statinfo = os.stat(pwd)
                try:
                    fd = os.open(pwd,os.O_RDONLY)
                except Exception as e:
                    print e
                    status = '404 NOT FOUND'
                msg = os.read(fd,statinfo.st_size)
                os.close(fd)
                filetype = GetFileType(pwd);                 
            
    return (msg,status,filetype) 


#######################
# aws_parse(rqst_wrds):
#
# Decodes each possible response from the AWS pinger
######################
def aws_parse(rqst_wrds):
    global pinger_list

    #When pingers turn on 
    if rqst_wrds[1] == 'Hello_World':

        pinger_list.append(rqst_wrds[3])
        pinger_list.append(rqst_wrds[5])

        msg = 'AWS WELCOME'

    #If main page was not found 
    if rqst_wrds[1] == 'SERVICE_ERROR': 
        msg  = '<html>'
        msg += '<body>'
        msg += '  <h1>Unknown Host \n </h1>'
        msg += '  <img src="https://wildknightsnark.files.wordpress.com/2012/09/you-are-here.jpg"/>' 
        msg += '</body>'
        msg += '</html>'

    #For geolocation 
    if rqst_wrds[1] == 'INFO':
        (loc,corr) = Decode_Region(rqst_wrds[8][:-1])
        msg  = '<html>'
        msg += '<body style="background-color:lightblue">'
        msg += '<h1> Geolocation Results </h1>'
        msg += '<h3> <u> Target Host </u>: ' + rqst_wrds[-1][7:] + '\n </h3>'
        msg += '<h3> <u> Closest Pinger </u>: ' + rqst_wrds[6] + '  (' + loc + ')' + '\n </h3>'
        msg += '<h3> <u> Minimum Connection Time </u>: ' + rqst_wrds[4] + 's \n </h3>'
        msg += ' <img src="http://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap&markers=color:red|'+str(corr[0]) + ',' +  str(corr[1])+ '&zoom=1"/>'
        msg += '</body>'
        msg += '</html>'

    return msg 

################################
#  parse(rqst):
#
# parse the orignial response and determines if its from 
# Amazon of another client. 
################################       
def parse(rqst):
    rqst_wrds = rqst.split()
    msg =''
    filetype = 'text/plain'

    #Check for kepp alive from project 1 
    keep_alive = False
    for i in range(0,len(rqst_wrds)-1):
        temp1=rqst_wrds[i].lower()
        temp2=rqst_wrds[i+1].lower()
        if temp1 == 'connection:' and temp2 == 'keep-alive':
            keep_alive = True; 
            break;

    #If Amazon 
    if rqst_wrds[0] == 'AWS':
        msg  = aws_parse(rqst_wrds) 
        rsp = msg 
    #If other client Get
    elif rqst_wrds[0] == 'GET':
        msg,status,filetype = client_parse(rqst_wrds)
        rsp = Create_Client_RSP(msg,status,filetype,keep_alive)
    #Not supported 
    else:
        status = '400 BAD REQUEST' 

    return (rsp,keep_alive)

############################
# ThreadFunction(conn):
#
# Threading function from project 1. Except pingers cant actually thread 
# because of the global variables (I think) so this isn't really implemented
###########################
def ThreadFunction(conn):
    keep_alive = True
    try: 
        while keep_alive:
            rqst  = conn.recv(5); 
            while (rqst[-4:] != '\r\n\r\n') and (rqst[-2:] != '\n\n'):
                ans= conn.recv(1); 
                if ans =='':
                    break
                else:
                    rqst += ans 
            print 'Got Request'
            rsp,keep_alive = parse(rqst)
            conn.sendall(rsp)
    except Exception as e: 
        print e

    conn.close()
    print 'Connection Closed'

#################################
# run_central_coordinator(central_host, central_port):
#
# Main function to run the central coordinator. 
################################
def run_central_coordinator(central_host, central_port):

    global dir_name
    dir_name = os.getcwd()

    global pinger_list
    pinger_list=[]
   
#   HOST = (central_host,central_port)
    HOST = ("",central_port)
    new_sck=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_sck.bind(HOST)
    new_sck.listen(1) 
    while 1:
        conn, addr = new_sck.accept()        
        print 'Got Connection from', addr
        t  = threading.Thread(target=ThreadFunction, args=(conn,))
        t.daemon = True
        t.start()
        
