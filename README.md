# Distributed Network and TCP Port Scanner with Web UI

[Description](https://www.securitee.org/teaching/cse509/projects/project2.html)

## Members : Script\_Buddies
* Raveendra Soori (raveendra.soori@stonybrook.edu)
* Sanjay Thomas (sanjay.mathewthomas@stonybrook.edu)
* Varun Hegde (varun.hegde@stonybrook.edu)

## Project Structure

Port-Scanner  
├── frontend              // Code for Front end lives here  
│   ├── index.js          // The start script  
│   ├── package.json  
│   ├── public            // public directory to serve files  
│   │   ├── loader.gif  
│   │   ├── main.css      // Front end CSS goes here  
│   │   └── script.js     // Front end scripts go here  
│   └── views  
│       └── index.ejs     // Default front end view which is rendered as HTML  
├── README.md  
└── worker                // The worker code goes here  
|   └── worker.py  

## Running

cd frontend  
npm install  
npm start  
  
Go to http://localhost:4321

## Credits

Icons by [Wichai.wi](https://www.flaticon.com/authors/wichaiwi)

