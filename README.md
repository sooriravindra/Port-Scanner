# Distributed Network and TCP Port Scanner with Web UI

[Description](https://www.securitee.org/teaching/cse509/projects/project2.html)

![alt text](https://github.com/sooriravindra/Port-Scanner/blob/master/System%20Sec.png)

## Members : Script\_Buddies
* Raveendra Soori (raveendra.soori@stonybrook.edu)
* Sanjay Thomas (sanjay.mathewthomas@stonybrook.edu)
* Varun Hegde (varun.hegde@stonybrook.edu)

  
## How to run the application?

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

  - **Redis** - docker run -p -d 6379:6379 redis
  - **MySQL Server** - docker run -v $PWD/mysql-data:/var/lib/mysql --name db -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123 mysql:latest
  - **Celery Workers** - sudo celery -A scanner worker
  - **Flask(for dev environment)** - python -m flask run


## Credits

* [Scapy](https://scapy.net/) Packet Crafting Library
* [Port Scanning](https://nmap.org/nmap_doc.html) Description of different port scanning techniques
* [Celery](http://www.celeryproject.org/) Distributed Task Queue
* [Flask](http://flask.pocoo.org/) Web Application
* [Emulating Nmap] https://thepacketgeek.com/scapy-p-10-emulating-nmap-functions/
* Icons by [Wichai.wi](https://www.flaticon.com/authors/wichaiwi)
