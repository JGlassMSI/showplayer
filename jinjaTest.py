from jinja2 import Environment, PackageLoader, select_autoescape
from flask import Flask, url_for

env = Environment(
	loader=PackageLoader('testApplication', 'templates'),
	autoescape=select_autoescape(['html', 'xml'])
	)

env.globals={'url_for': url_for}