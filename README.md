# Distributed Network and TCP Port Scanner with Web UI

[Description](https://www.securitee.org/teaching/cse509/projects/project2.html)

![alt text](https://github.com/sooriravindra/Port-Scanner/blob/master/Block%20Diagram.png)

## Members : Script\_Buddies
* Raveendra Soori (raveendra.soori@stonybrook.edu)
* Sanjay Thomas (sanjay.mathewthomas@stonybrook.edu)
* Varun Hegde (varun.hegde@stonybrook.edu)

## Flow
  - Request Handler boots up
  - Workers register with the request handler
  - Upon successful registration the workers are assigned with a unique id.
  - User submits a port scanning request to the request handler
  - Request handler upon receiving the port scanning request distributes the jobs among the free workers.
  - The workers upon finishing the task submit the results onto a common channel.
  - The request handler upon receiving the port scanning response emits the results onto a channel which the web ui listens    to.
  - The web ui renders the port scanning result upon receiving the response.

## Project Structure

Port-Scanner/  
├── README.md  
├── router //Crossbar router and web application UI  
│   ├── Dockerfile  
│   └── web  
│   .    ├── favicon.ico  
│   .    ├── index.html // HTML frontend  
│   .    ├── loader.gif  
│   .    ├── logo.png  
│   .    ├── script.js // JS for frontend  
│   .    └── main.css  
└── scanner //Port scanning code, request handlers and workers.  
.   ├── request\_handler.py  
.   ├── scanner.py  
.   ├── test.py  
.   └── worker.py  
  
## Run the code

```
   # Start Redis
   docker run -p -d 6379:6379 redis 
   # Start MySQL
   docker run -v $PWD/mysql-data:/var/lib/mysql --name db -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123 mysql:latest
   #To enter mysql server 
   docker exec -it db /bin/bash
   cd scanner 
   #Start Celery Worker
   sudo celery -A scanner worker
   #Start Flask
   python -m flask run
```

## Credits

* [Scapy](https://scapy.net/) packet crafting library.
* Icons by [Wichai.wi](https://www.flaticon.com/authors/wichaiwi)
