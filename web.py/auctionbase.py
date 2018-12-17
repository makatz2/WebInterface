#!/usr/bin/env python

# Authors:
# Name: Michael Katz, ID: 9070102042
# Name: Emmet Ryan, ID: 9069927185
# Name: Kshitij Kumar, ID: 9079574746

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/addbid', 'add_bid',
        '/search', 'search_func',
        '/itemPage', 'item_page'
        # first parameter => URL, second parameter => class name
        )

class item_page:
    def GET(self):
        itemID = web.input().id
        itemDetails = sqlitedb.getItemById(itemID)
        bids = sqlitedb.getItemBids(itemID)
        categories = sqlitedb.getItemCats(itemID)
        winner = sqlitedb.getItemWinner(itemID)
        bStatus = sqlitedb.getItemStatus(itemID)
#        if bStatus != 0:
#            bStatus = "Open"
#        else:
#            bStatus = "Closed"
        return render_template('item_page.html',item_id=itemID, item_details=itemDetails, item_bids = bids, item_cats = categories, item_winner = winner, item_status = bStatus)



        return render_template('item_view.html')
class search_func:
    def GET(self):
        return render_template('search.html')

    def POST(self):
        post_params = web.input()
        results = sqlitedb.search(post_params['itemID'], 
            post_params['userID'], post_params['category'], 
            post_params['description'], post_params['minPrice'],
            post_params['maxPrice'], post_params['status'])
        return render_template('search.html', search_result = results)

class add_bid:
    def GET(self):
        return render_template('add_bid.html')
    def POST(self):
        try:
            post_params = web.input()
            userID = post_params['userID']      
            itemID = post_params['itemID']
            price = post_params['price']
            currTime = sqlitedb.getTime();

            item = sqlitedb.getItemById(itemID);
            itemPrice = item['Currently']
            itemEndTime = item['Ends']
            ItemStartTime = item['Started']
            buyPrice = item['Buy_Price']
            if price <= itemPrice:
                update_message ='(Hi %s, your bid of %s on item %s was unsuccessful because the current bid was higher than your bid.)' % (userID, itemID, price)
            elif currTime > itemEndTime or buyPrice <= itemPrice:
                update_message ='(Hi %s, your bid of %s on item %s was unsuccessful because the auction for this item has ended.)' % (userID, itemID, price)
            elif currTime < itemStartTime:
                update_message ='(Hi %s, your bid of %s on item %s was unsuccessful because the auction for this item has not started yet.)' % (userID, itemID, price)
            else:
                sqlitedb.addBid(userID, itemID, price)
                update_message = '(Hi %s, your bid of %s on item %s was successful!)' % (userID, itemID, price)
        except Exception as e:
            update_message = '(A database error occured: %s)' % (e.message)
        return render_template('add_bid.html', message = update_message)

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time);
        sqlitedb.setTime(string_to_time(selected_time))

        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()

