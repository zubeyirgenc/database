import os
import sys
import psycopg2 as dbapi2
from passlib.handlers.pbkdf2 import pbkdf2_sha256 as hasher



INIT_STATEMENTS = [
    """
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;
    """,

    """CREATE TABLE IF NOT EXISTS ADDRESS (
        ID              SERIAL PRIMARY KEY,
        ADDRESS_NAME    VARCHAR(30),
        COUNTRY         VARCHAR(30) NOT NULL,
        CITY            VARCHAR(30) NOT NULL,
        DISTRICT        VARCHAR(30),
        NEIGHBORHOOD    VARCHAR(30),
        AVENUE          VARCHAR(30),
        STREET          VARCHAR(30),
        ADDR_NUMBER     VARCHAR(10),
        ZIPCODE         CHAR(5),
        EXPLANATION     VARCHAR(500)
    )  """,
    
        """
    CREATE TABLE IF NOT EXISTS WEBUSER (
        ID              SERIAL PRIMARY KEY,
        PASSWORD_HASH   VARCHAR(256) NOT NULL,
        EMAIL           VARCHAR(50) NOT NULL UNIQUE,
        NAME            VARCHAR(50) NOT NULL,
        SURNAME         VARCHAR(50) NOT NULL,
        IS_ACTIVE       BOOLEAN DEFAULT TRUE,
        CREATED_DATE    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )  """,

        """
    CREATE TABLE IF NOT EXISTS ADMIN (
        ID              SERIAL PRIMARY KEY,
        PHONE_NUM       VARCHAR(30) NOT NULL,
        ADMIN_PASSWORD  VARCHAR(256) NOT NULL,
        ADDRESS_REF     INTEGER REFERENCES ADDRESS (ID),
        WEBUSER_REF     INTEGER NOT NULL REFERENCES WEBUSER (ID)
    )  """,

    """CREATE TABLE IF NOT EXISTS MEMBER (
        ID              SERIAL PRIMARY KEY,
        CONFIRM_DATE    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONFIRMED_BY    INTEGER REFERENCES ADMIN (ID),
        WEBUSER_REF     INTEGER NOT NULL REFERENCES WEBUSER (ID)
    )""",

    """
    CREATE TABLE IF NOT EXISTS TRANSAC (
        ID              SERIAL PRIMARY KEY,
        CREATED_DATE    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        AMOUNT          SMALLINT NOT NULL,
        CREATED_BY      INTEGER NOT NULL REFERENCES WEBUSER (ID),
        CONFIRMED_BY    INTEGER REFERENCES ADMIN (ID),
        DELETED_BY      INTEGER REFERENCES ADMIN (ID),
        IS_DEL          BOOLEAN DEFAULT FALSE
    )""",

    """CREATE TABLE IF NOT EXISTS DEBT (
        ID              SERIAL PRIMARY KEY,
        TR_REF          INTEGER NOT NULL REFERENCES TRANSAC (ID),
        START_PREIOD    TIMESTAMP NOT NULL,
        DUE_PERIOD      TIMESTAMP NOT NULL,
        NUMBER_PAY      SMALLINT NOT NULL,
        AMOUNT_PAY      SMALLINT NOT NULL DEFAULT 0,
        PAID            SMALLINT NOT NULL DEFAULT 0
    )""",

    """CREATE TABLE IF NOT EXISTS PAYMENT (
        ID              SERIAL PRIMARY KEY,
        DEBT_REF        INTEGER DEFAULT NULL DEBT (ID),
        PAY_NUM         SMALLINT,
        TR_REF          INTEGER NOT NULL REFERENCES TRANSAC (ID)
    )""",
    ]

def initialize(url2):
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:# as cursor:
            for statement in INIT_STATEMENTS:
                print("SQL Run:", statement)
                cursor.execute(statement)

def insert(url2, PASSWORD_HASH, EMAIL, NAME, SURNAME):

    GEN_INSERT = "INSERT INTO WEBUSER (PASSWORD_HASH, EMAIL, NAME, SURNAME) VALUES (%s, %s, %s, %s)"
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(GEN_INSERT, (PASSWORD_HASH, EMAIL, NAME, SURNAME, ))
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass

def initial(url2):

    WEBUSER_INSERT = "INSERT INTO WEBUSER (PASSWORD_HASH, EMAIL, NAME, SURNAME) VALUES (%s, %s, %s, %s) returning id"
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            password_hash = hasher.hash("form.password.data")
            try:
                cursor.execute(WEBUSER_INSERT, (password_hash, "admin@admin.com", "admin", "admin", ))
                # cursor.lastrowid
                # WEBUSER_FETCH = """SELECT * FROM WEBUSER WHERE email = %s"""
                # cursor.execute(WEBUSER_FETCH, ("admin@admin.com",))
                webuser = cursor.fetchone()
                print(webuser)
                # cursor.commit()
                # webuser = cursor.lastrowid#cursor.fetchone()

                ADDRESS_INSERT = "INSERT INTO ADDRESS (COUNTRY,CITY) VALUES (%s, %s) returning id"
                cursor.execute(ADDRESS_INSERT, ("COUNTRY","CITY", ))
                # ADDRESS_FETCH = """SELECT * FROM ADDRESS WHERE country = %s"""
                # cursor.execute(WEBUSER_FETCH, ("COUNTRY",))
                # cursor.commit()
                # address = cursor.lastrowid#cursor.fetchone()
                address = cursor.fetchone()


                admin_hash = hasher.hash("admin")
                ADMIN_INSERT = "INSERT INTO ADMIN (PHONE_NUM,ADMIN_PASSWORD,ADDRESS_REF,WEBUSER_REF) VALUES (%s, %s, %s, %s)"
                cursor.execute(ADMIN_INSERT, ("05447815548", admin_hash, address[0], webuser[0], ))


                # webuser[0]
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass  


if __name__ == "__main__":

    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
    insert(url, "PASSWORD_HASH", "EMAIL", "NAME", "SURNAME")
    initial(url)

DELETE FROM TRANSAC WHERE ID=7;
SELECT * FROM TRANSAC 