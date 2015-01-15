from paste.deploy import loadapp

application = loadapp('config:prod.ini', relative_to='.')
