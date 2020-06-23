import pymysql



def get_connection():
    connection = pymysql.connect(host='localhost',
									user='scrapy',
									password='Cosmos1',
									db='blogs',
									charset='utf8mb4',
									use_unicode=True,
									cursorclass=pymysql.cursors.DictCursor)
    # connection = pymysql.connect(host='144.167.35.221',
    #                             user='diffbot',
    #                             password='Cosmos1',
    #                             db='blogs',
    #                             charset='utf8mb4',
    #                             use_unicode=True,
    #                             cursorclass=pymysql.cursors.DictCursor)
    return connection

def commit_to_db(query, data, error=0):
    # while True: 
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
                cursor.execute(query, data)
                connection.commit()
                connection.close()
                return 
    #Error handeling
    except Exception as e:
        if isinstance(e, pymysql.err.IntegrityError) and e.args[0]==1062:
            # Duplicate Entry, already in DB
            if 'INTO posts' in query:
                pass #Duplicate posts will happen, they don't need to be udpated
            else: 
                print("There is already duplicate entry in the DB, check the quary: {}".format(query))
            connection.close() 
            return
        elif e.args[0] == 1406:
            # Data too long for column
            print(e)
            print("Good API request, but data is Too Long for DB Column")
            connection.close()
            return 
        elif e.args[0] == 2013:
            if error < 10:
                commit_to_db(query, data, error+1)
                connection.close()
            else:
                raise Exception("Keep loosing connection to the db: {}".format(e))
        else: 
            # Uncaught errors
            raise Exception("We aren't catching this mySql commit_to_db Error: {}".format(e))
