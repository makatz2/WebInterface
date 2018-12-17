# Authors:
# Name: Michael Katz, ID: 9070102042
# Name: Emmet Ryan, ID: 9069927185
# Name: Kshitij Kumar, ID: 9079574746
import web

db = web.database(dbn='sqlite',
        db='AuctionBase' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()

# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples
def search(item_ID, user_ID, Category, description, min_price, max_price, status):
    first = True

    allVars = {}
    
    if Category:
        allVars.update({'category': Category});
        query_string = 'SELECT * FROM Items I JOIN Categories C WHERE C.ItemID = I.ItemID AND C.Category = category';
        first = None
    else:
        query_string = 'select * from Items I'
    if item_ID:
        if first:
            query_string += ' WHERE'
            first = None
        else:
            query_string += ' AND'
        allVars.update({'itemID': item_ID});
        query_string += ' I.ItemID = $itemID';
    if user_ID:
        if first:
            query_string += ' WHERE'
            first = None
        else:
            query_string += ' AND'
        allVars.update({'userID': user_ID});
        query_string += ' I.Seller_UserID = $userID';
    if description:
        if first:
            query_string += ' WHERE'
            first = None
        else:
            query_string += ' AND'
        allVars.update({'Description': '%' + description + '%'})
        query_string += ' I.Description LIKE $Description';
    if min_price:
        if first:
            query_string += ' WHERE'
            first = None
        else:
            query_string += ' AND'
        allVars.update({'minPrice': min_price});
        query_string += ' I.Currently > $minPrice';
    if max_price:
        if first:
            query_string += ' WHERE'
            first = None
        else:
            query_string += ' AND'
        allVars.update({'maxPrice': max_price});
        query_string += ' I.Currently = $maxPrice';
    currTime = getTime();
    allVars.update({'currentTime': currTime});
    if status != 'all':
        if first:
            query_string += ' WHERE'
            first = None
        else:
            query_string += ' AND'
    if status == 'close':
        query_string += ' I.Ends < $currentTime OR I.Buy_Price == I.Currently';
    elif status == 'open':
        query_string += ' I.Ends > $currentTime AND I.Started < $currentTime';
    elif status == 'notStarted':
        query_string += ' I.Started > $currentTime';

    t = db.transaction()
    try:
        results = query(query_string, allVars)
    except Exception as e:
        t.rollback()
        return False
    else:
        t.commit();
        return results
    
#if(item_ID != null)
# returns the current time from your database
def getTime():
    # DONE_TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select Time from CurrentTime'
    results = query(query_string,{})
    # alternatively: return results[0]['currenttime']
    return results[0]['Time'] # DONE_TODO: update this as well to match the
                                  # column name

# updates the currentTime based on user provided value
def setTime(user_time):
    db.update('CurrentTime', where = "1 == 1", Time = user_time)
    return

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!

def addBid(Price, item_ID, user_ID):
    t = db.transaction()
    try: 
        db.insert('Bids', ItemID = item_ID, UserID = user_ID, Amount = Price, Time = getTime())
    except Exception as e:
        t.rollback()
        return False
    else:
        t.commit()
        return True

def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result[0]

def getItemBids(item_id):
    query_string = 'select * from Bids where ItemID = $itemID Order By Time desc'
    result = query(query_string, {'itemID': item_id})
    return result


def getItemCats(item_id):
    query_string = 'select * from Categories where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result

def getItemWinner(item_id):
    cTime = getTime()
    query_string = 'select UserID from Bids B, Items I WHERE B.ItemID = $itemID AND (SELECT Time FROM CurrentTime) >= I.Ends Order by Time desc LIMIT 1;'
    result = query(query_string, {'itemID': item_id})
    return result       

def getItemStatus(item_id):
	query_string = 'select COUNT(*) from Items I WHERE I.ItemID = $itemID AND (SELECT Time from CurrentTime) >= I.Ends'
	result = query(query_string, {'itemID': item_id})
	return result

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
