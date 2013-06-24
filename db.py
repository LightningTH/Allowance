import sys
import sqlite3

def sanitize(**params):
	for Entry in params:
		if(type(params[Entry]) is str):
			params[Entry] = params[Entry].replace("<","&lt;")
			params[Entry] = params[Entry].replace(">","&gt;")
			params[Entry] = params[Entry].replace("'","&#039;")
			params[Entry] = params[Entry].replace("\"","&quot;")
			params[Entry] = params[Entry].replace("{","&#123;")
			params[Entry] = params[Entry].replace("}","&#125;")
			params[Entry] = params[Entry].replace("[","&#091;")
			params[Entry] = params[Entry].replace("]","&#093;")
			params[Entry] = params[Entry].strip()
	return params

def fetchAll(conn, query, keys=None):
	ret = True
	results = dict()
	sys.stdout.flush()
	cur = conn.cursor()
	try:
		if(keys == None):
			cur.execute(query)
		else:
			cur.execute(query, keys)
		results = cur.fetchall()
	except Exception as e:
		print e
		sys.stdout.flush()
		ret = False

	if results is None:
		ret = False

	return (ret, results)

def fetchOne(conn, query, keys=None):
	ret = True
	results = dict()
	sys.stdout.flush()
	cur = conn.cursor()
	try:
		if(keys == None):
			cur.execute(query)
		else:
			cur.execute(query, keys)
		results = cur.fetchone()
	except Exception as e:
		sys.stdout.flush()
		ret = False

	if results is None:
		ret = False

	return (ret, results)

def execute(conn, query, *args):
	ret = True
	results = dict()
	cur = conn.cursor()
	row_count = 0
	try:
		cur.execute(query, *args)
		row_count = cur.rowcount
		conn.commit()
	except Exception as e:
		print "ERROR WITH QUERY '", query,"' : ", e
		sys.stdout.flush()

	return row_count

def make_connect():
	print "Making a new database connection"
	return sqlite3.connect('/home/lightning/money.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

