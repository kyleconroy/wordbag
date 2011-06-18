#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import os
import random
from django.utils import simplejson as json
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util


TILES = [
    ("", "", 2),
    ("A", 1, 9),
    ("B", 3, 2),
    ("C", 3, 2),
    ("D", 2, 4),
    ("E", 1, 12),
    ("F", 4, 2),
    ("G", 2, 3),
    ("H", 4, 2),
    ("I", 1, 9),
    ("J", 8, 1),
    ("K", 5, 1),
    ("L", 1, 4),
    ("M", 3, 2),
    ("N", 1, 6),
    ("O", 1, 8),
    ("P", 3, 2),
    ("Q", 10, 1),
    ("R", 1, 6),
    ("S", 1, 4),
    ("T", 1, 6),
    ("U", 1, 4),
    ("V", 4, 2),
    ("W", 4, 2),
    ("X", 8, 1),
    ("Y", 4, 2),
    ("Z", 10, 1),
    ]


class Game(db.Model):
    pass


class Bag(object):

    def __init__(self):
        bag = []

        for tile in TILES:
            for i in range(tile[2]):
                bag.append({"letter": tile[0], "value": tile[1]})

        self.bag = bag

    def draw(self):
        random.shuffle(self.bag)

        if len(self.bag):
            return self.bag.pop()
        else:
            return None

    def size(self):
        return len(self.bag)


class MainHandler(webapp.RequestHandler):

    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {}))


class GamesHandler(webapp.RequestHandler):

    def post(self):
        game = Game()
        game.put()
        key = str(game.key())

        if not memcache.add(key, Bag()):
            logging.error("Memcache set failed.")

        # Create new memcache entry
        self.redirect("/games/%s" % game.key())


class GameHandler(webapp.RequestHandler):

    def get(self, game_id):
        path = os.path.join(os.path.dirname(__file__), 'game.html')
        self.response.out.write(template.render(path, {"game_key": game_id}))


class BagHandler(webapp.RequestHandler):

    def get(self, game):
        bag = memcache.get(game)

        output = {
            "size": bag.size(),
        }

        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(output))

    def post(self, game):
        bag = memcache.get(game)
        letter = bag.draw()

        if not memcache.set(game, bag):
            logging.error("Memcache set failed.")

        letter["size"] = bag.size()
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(letter))


def main():

    ROUTES = [
        ('/', MainHandler),
        ('/games', GamesHandler),
        ('/games/(.*)/bag', BagHandler),
        ('/games/(.*)', GameHandler),
    ]

    application = webapp.WSGIApplication(ROUTES, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
