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
def search(item_ID, user_ID, Category, min_price, max_price, status):
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
		print 'here1'
		if first:
			query_string += ' WHERE'
			first = None
		else:
			query_string += ' AND'
	if status == 'close':
		query_string += ' I.Ends < $currentTime';
	elif status == 'open':
		query_string += ' I.Ends > $currentTime AND I.Started < $currentTime';
	elif status == 'notStarted':
		query_string += ' I.Started > $currentTime';

	results = query(query_string, allVars)
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
	# query_string = 'UPDATE CurrentTime SET Time = $userTime'
	# query(query_string, {'userTime': user_time})
	t = transaction();
	try:
		db.update('CurrentTime', where='1=1', Time='$userTime', vars={'userTime': user_time})
	except Exception as e:
		t.rollback()
		print str(e)

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!

def addBid(Price, item_ID, user_ID):
    currTime = getTime();
    query_string = 'INSERT INTO Bids (ItemID, UserID, Amount, Time) VALUES ($itemID, $userID, $price, $time)'
    result = query(query_string, {'itemID': item_ID, 'userID': user_ID, 'price': Price, 'time': currTime})

def getItemById(item_id):
    # DONE_TODO: rewrite this method to catch the Exception in case `result' is empty
    try:
        query_string = 'select * from Items where Item_ID = $itemID'
        result = query(query_string, {'itemID': item_id})
    except Exception as e:
        t.rollback()
        print str(e)
    return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
