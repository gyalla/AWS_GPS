# Amazon Web Services - Global Positioning Systems (AWS-GPS)

AWS-GPS is a simple geolocation tool for Amazon Web Services. By measuring ping times to different AWS servers, this
software is able to approximate the location of a host to the nearest server. One server acts as a the central point of 
communication, which the client interacts with directly; the other servers are 'pingers' that only communicate with the central server. 
Once the client gives the central serve a hostname through the web interface, the central server tells the pingers to ping 
the hostname and report back times. The pinger with the shorest ping time is choosen as the nearest location to the host. 

## Getting Started

To make use of AWS-GPS you need to have at least two EC2 instances running in a VPC on Amazon Web Services. Suppose the there are three instanace running on AWS labeled 
ec2-center.compute.amazonaws.com, ec2-pinger1.compute.amazonaws.com, ec2-pinger1.compute.amazonaws.com. First run 

```
git clone https://github.com/gyalla/AWS_GPS.git
```
on all three servers. Then run, 

```
./geolocate.py ec2-center.compute.amazonaws.com 3000
```
on the central server followed by all the pingers to launch the geolocator on port 3000 (any available port can be choosen). The pingers will display an activation notice if successful. 
Go to ec2-center.compute.amazonaws.com:3000 on a web browser and enter a host. The central server will contact the pinger, which will ping the hostname and report back ping times. The central
server will display the location of the nearest pinger server. 


## Authors

* **Gopal Yalla**

Initial work started as part of Dr. Kevin Walsh's Computer Networking course at College of the Holy Cross. 
Much thanks to Dr. Walsh for his continued support at Holy Cross and start up work with this project. 

## Notes 

As amazon expands availability zones, they need to be added to the geolocator or the pingers will return an unknown location. They can be easily added in central.py.
