const express = require('express')
const path = require('path')
const server_port = 4321

function render_default(req, res) {
    res.render('index');
}

express()
    .use(express.static(path.join(__dirname, 'public')))
    .set('views', path.join(__dirname, 'views'))
    .set('view engine', 'ejs')
    .get('/', render_default)
    .listen(server_port, () => (console.log("Listening on port " + server_port)));
