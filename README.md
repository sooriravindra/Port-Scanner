# Distributed Network and TCP Port Scanner with Web UI

[Description](https://www.securitee.org/teaching/cse509/projects/project2.html).

![alt text](https://github.com/sooriravindra/Port-Scanner/blob/master/BlockDiagram.png)

## Members : Script\_Buddies
* Raveendra Soori (raveendra.soori@stonybrook.edu)
* Sanjay Thomas (sanjay.mathewthomas@stonybrook.edu)
* Varun Hegde (varun.hegde@stonybrook.edu)

## Project Files

Some of the important files to look at are:

- scanner/app.py - Web Application endpoints
- scanner/scanner.py - Actual port scanning code.
- scanner/db.py - Utilities to query data from the database.
- docker-compose.yml - Docker Compose config.
  
## How to run the application?

**Note** : Please use a modern browser preferably later versions of Chrome to support Javascript ES6 syntax.

- If you quickly want to get started docker-compose is the suggested solution. We **highly recommend** you to use to deploy it by using docker compose.

```
   Install docker and docker-compose
   docker-compose build
   docker-compose up -d
   <!-- to stop all containers -->
   docker compose down
```

  Application can be accessed on the http://localhost:5001/

- You could deploy individual components seperately too, if you feel a little adventurous.

  - **Redis** - docker run -d -p 6379:6379 redis
  - **MySQL Server** - docker run -v $PWD/mysql-data:/var/lib/mysql --name db -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123 mysql:latest
  - **Celery Workers** - sudo celery -A scanner worker
  - **Flask(for dev environment)** - python -m flask run
  - Create additional tables, if you face trouble creating the tables directly import the SQL script in dump.sql.
  
  ```DROP TABLE IF EXISTS `master_tasks`;
      CREATE TABLE `master_tasks` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `ip_address` varchar(45) NOT NULL,
        `start_port` int(11) NOT NULL,
        `end_port` int(11) NOT NULL,
        `subnet` varchar(45) NOT NULL,
        `task_type` varchar(45) NOT NULL,
        PRIMARY KEY (`id`)
    );

  DROP TABLE IF EXISTS `celery_tasks`;
   CREATE TABLE `celery_tasks` (
    `task_id` text NOT NULL,
    `master_task_id` int(11) DEFAULT NULL
  );```


## Ping Scan

Involves connecting to a remote host using a ICMP request, and if the response received is not of the type Destination Unreachable(Type 3) then the host is said to alive. To confirm if the host is really down we  scan the ports running common services such as SSH, DNS, HTTP etc. A response other than a RST would confirm that the host is alive.

## Full TCP Connect and Banner Grabbing

Involves connect to a remote host on a specific port using the connect system call, and further sending appropriate input on the established connection to find out more about the services running on these open ports.

## Syn Scan

Send the TCP packet to the remote host with only the SYN flag set, if the response received is SYN|ACK we know that the port is open. If we receive a RST then the port is closed. 

## Fin Scan

Send the TCP packet to the remote host with only the FIN flag set, if the response received is RST we know that the port is closed. The assumption is that is that open ports do not send a response to a FIN scan. Hosts which sends RST regardless of the port state are not vulnerable to this type of attack.  


## Credits

* [Scapy](https://scapy.net/) Packet Crafting Library
* [Port Scanning](https://nmap.org/nmap_doc.html) Description of different port scanning techniques
* [Celery](http://www.celeryproject.org/) Distributed Task Queue
* [Flask](http://flask.pocoo.org/) Web Application
* [WaitForIt](https://github.com/vishnubob/wait-for-it) Script to wait for availibility of a host.
* [Emulating Nmap] https://thepacketgeek.com/scapy-p-10-emulating-nmap-functions/
* Icons by [Wichai.wi](https://www.flaticon.com/authors/wichaiwi)
