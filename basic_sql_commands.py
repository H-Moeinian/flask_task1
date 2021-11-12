import pymssql


def create_users_table():
    conn = pymssql.connect(server='127.0.0.1', database="diver")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE Users ("
                   "Username varchar(30) NOT NULL PRIMARY KEY,"
                   "Password varchar(102) NOT NULL,"
                   "LastName varchar(50),"
                   "FirstName varchar(50),"
                   "Age tinyint,"
                   "City varchar(50));")
    conn.commit()
    conn.close()

def insert_test_users():
    conn = pymssql.connect(server='127.0.0.1', database="diver")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users VALUES"
                   "('09121111111',"
                   "'pbkdf2:sha256:260000$HXgq3uX6ErI4IIPR$db8d16be1a21216a10292afee84edd692d17d4b09e559cea6d8f2edba954e774'"
",'ahmadi','ahmad',20,'tehran'),"
                   "('09191111111',"
                   "'pbkdf2:sha256:260000$2KrXoFnFr1Pg7Com$3f5a97ff5e02d6f20768cc03242f3c3ad936209e766ec8966244bb786d830777'"
",'mohammadi','mohammad',30,'karaj');")
    conn.commit()
    conn.close()


def create_stored_procedure():
    conn = pymssql.connect(server='127.0.0.1', database="diver")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE PROCEDURE write_profile @lastname VARCHAR(50), @firstname VARCHAR(50),
    @age tinyint, @city VARCHAR(50),
    @username VARCHAR(30)
    AS
    BEGIN
    UPDATE Users SET Lastname=@lastname,Firstname=@firstname,Age=@age,City=@city WHERE Username=@username;
    END;""")
    conn.commit()
    conn.close()


create_users_table()
insert_test_users()
create_stored_procedure()