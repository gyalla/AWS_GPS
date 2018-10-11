#!/usr/bin/python
#############################################################
# Gopal Yalla
# 3/20/2015
# Purpose: Implementation of the pinger server for geolocation service
#############################################################
import socket
import threading
import time
import random


############################################
# Start_Up(central_host,central_port,dns_name,region):
#
# When the pingers start up, they connect with the central server 
# to get added to the list 
###########################################
def Start_Up(central_host,central_port,dns_name,region):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #Try 5 times 
    for i in range (0,5):
        try:
            client_socket.connect((central_host,central_port)) 
            break
        except Exception as e:
            print e

    rqst  = 'AWS Hello_World \r\n'
    rqst += 'DNS: ' + dns_name + '\r\n'
    rqst += 'REGION: ' + region + '\r\n\r\n'

    client_socket.send(rqst);
    rsp = client_socket.recv(2048);
    return rsp


##############################
# parse(rqst,dns_name,region):
#
# Parses different requests from the client
#############################
def parse(rqst,dns_name,region):

    rqst_wrds = rqst.split()
    
    # If the client wants to check if the pigner is still there
    # Used for page refresh
    if rqst_wrds[1] == 'HELLO':
        rsp = "AWS HELLO"
    
    #Requests information from Target 
    elif rqst_wrds[0] == 'AWS':
        
        print 'Retriving information'
       
        #Formality with urlparse if user doesn't enter full url 
        if rqst_wrds[1][0:7] != 'http://':
            rqst_wrds[1] = 'http://' + rqst_wrds[1]; 
        
        from urlparse import urlparse
        URL = urlparse(rqst_wrds[1])
        
        #Ping target 5 times 
        try: 
            rqst  = 'GET /' + URL.path  + ' HTTP/1.1\r\n'
            rqst += 'Host: ' + dns_name + '\r\n\r\n' 
            min_time = 10; 
            for i in range(0,5):
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((URL.netloc,80))      

                time.sleep(random.uniform(0.25, 1.0))
                start = time.time()
                try: 
                    client_socket.sendall(rqst)
                    rsp1 = client_socket.recv(1);
                    end = time.time()
                    rsp1 = client_socket.recv(100000); 
                    total_time = end-start;
                    if total_time < min_time: 
                        min_time = total_time
                except Exception as e:
                    print e
                        
            rsp  = 'AWS INFO \r\n'
            rsp += 'Total Time: ' + str(min_time) + '\r\n'
            rsp += 'DNS: ' + dns_name + '\r\n'
            rsp += 'REGION: ' + region + '\r\n'
            rsp += 'Target: ' + rqst_wrds[1] + '\r\n\r\n'

        #If host can't be found..error
        except:
            rsp = "AWS SERVICE_ERROR"

    #Nothing else is supported 
    else:
        rsp = 'HTTP/1.1 400 BAD REQUEST \r\n\r\n'
    return rsp

#Attempt at threading function which didn't work becuase of 
#all the global variables..I think 
#def ThreadFunction(conn,dns_name,region):
#    rqst=conn.recv(2048)
#    rsp = parse(rqst,dns_name,region)
#    conn.sendall(rsp)
#    conn.close()
        

############################
# run_pinger_server(dns_name, region,port,central_host, central_port)
#
# Runs the pinger server 
###############################
def run_pinger_server(dns_name, region,port,central_host, central_port):
    time.sleep(2) 
    rsp = Start_Up(central_host,central_port,dns_name,region)
    
    #Checks connection to central host 
    if rsp == 'AWS WELCOME':
        print 'Pinger Activated'
    else:
        print 'No Connection to Central Host'
        sys.exit(1)
    

    HOST=("",port);
    new_sck=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_sck.bind(HOST)
    new_sck.listen(1) 
    while 1:
        conn, addr = new_sck.accept()        
        rqst=conn.recv(2048)
        rsp = parse(rqst,dns_name,region)
        conn.sendall(rsp)
        conn.close()
#        t = threading.Thread(target=ThreadFunction, args=(conn,dns_name,region))
#        t.daemon = True 
#        t.start
