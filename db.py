import os
import sys
import psycopg2 as dbapi2
from flask import current_app
import models

# DROP SCHEMA public CASCADE;
# CREATE SCHEMA public;
def update(email=None, password_hash=None, name=None,surname=None):
    guncellenecekler = []

    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()

        query = """UPDATE WebUser SET """
        if name:
            query += "name = %s, "
            guncellenecekler.append(name)
        if surname:
            query += "surname = %s, "
            guncellenecekler.append(surname)
        if password_hash:
            query += "password_hash = %s, "
            guncellenecekler.append(password_hash)
        query = query[:-2] + " "
        query += "WHERE EMAIL = %s"
        guncellenecekler.append(email)

        try:
            cursor.execute(query, tuple(guncellenecekler))
            # webuser = cursor.fetchone()
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    # return webuser

def get_webuser(email=None, id=None):
    asd = []
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()

        query = """SELECT * FROM WebUser WHERE """
        if email:
            query += "email = %s, "
            asd.append(email)
        if id:
            query += "id = %s, "
            asd.append(id)
        query = query[:-2] + " ORDER BY ID"

        try:
            cursor.execute(query, tuple(asd))
            webuser = cursor.fetchone()
            if webuser:
                webuser_obj = models.WebUser(webuser)
            else:
                webuser_obj = None

        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return webuser_obj

def get_member(webuser_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM MEMBER WHERE WEBUSER_REF = %s   ORDER BY ID"""

        try:
            cursor.execute(query, (webuser_id,))
            member = cursor.fetchone()
            if member:
                member_obj = models.Member(member)
            else:
                member_obj = None

        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return member_obj

def get_members():
    members_obj = []
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM MEMBER   ORDER BY ID"""
        try:
            cursor.execute(query, tuple())
            members = cursor.fetchall()
            for member in members:
                members_obj.append(models.Member(member))

        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return members_obj

def get_admin(webuser_id=None,admin_id=None):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        if webuser_id:
            query = """SELECT * FROM Admin WHERE webuser_ref = %s   ORDER BY ID"""
        else:
            query = """SELECT * FROM Admin WHERE id = %s   ORDER BY ID"""            
        try:
            cursor.execute(query, (webuser_id or admin_id,))
            admin = cursor.fetchone()
            if admin:
                webuser_obj = get_webuser(id=admin[4])
                address_obj = get_address(ID=admin[3])
                admin_obj = (models.Admin(admin,webuser_obj,address_obj))
            else:
                admin_obj = None
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return admin_obj

def insert(PASSWORD_HASH, EMAIL, NAME, SURNAME):
    url2 = current_app.config["database_url"]
    GEN_INSERT = "INSERT INTO WEBUSER (PASSWORD_HASH, EMAIL, NAME, SURNAME) VALUES (%s, %s, %s, %s)"
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(GEN_INSERT, (PASSWORD_HASH, EMAIL, NAME, SURNAME, ))
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass

def get_webusers_unconfirmed():
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()        
        query = """SELECT * FROM WebUser WHERE ID NOT IN (SELECT WEBUSER_REF FROM MEMBER) AND ID NOT IN (SELECT WEBUSER_REF FROM ADMIN)  ORDER BY ID"""
        try:
            cursor.execute(query)
            webusers = cursor.fetchall()
            webusers_obj = []
            for webuser in webusers:
                webusers_obj.append(models.WebUser(webuser))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return webusers_obj

def insert_member(admin_id,webuser_id):
    url2 = current_app.config["database_url"]
    GEN_INSERT = "INSERT INTO MEMBER (CONFIRMED_BY, WEBUSER_REF) VALUES (%s, %s)"
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(GEN_INSERT, (admin_id, webuser_id,))
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass

def insert_transaction(amount,webuser_id):
    url2 = current_app.config["database_url"]
    GEN_INSERT = "INSERT INTO TRANSAC (AMOUNT, CREATED_BY) VALUES (%s, %s) returning id "
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(GEN_INSERT, (amount, webuser_id,))
                id = cursor.fetchone()[0]
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass
    return id

def insert_debt(transaction_id,due_period,start_period,number_pay):
    url2 = current_app.config["database_url"]
    GEN_INSERT = "INSERT INTO DEBT (TR_REF, DUE_PERIOD, START_PREIOD, NUMBER_PAY) VALUES (%s, %s, %s, %s)"
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(GEN_INSERT, (transaction_id, due_period, start_period, number_pay))
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass

def get_debts(webuser_id=None,id=None):
    debt_list = []
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        if webuser_id:
            query = """SELECT * FROM TRANSAC,DEBT WHERE TRANSAC.ID=DEBT.TR_REF and transac.created_by=%s ORDER BY ID(DEBT)"""
            """SELECT TRANSAC.*,DEBT.*,COUNT(*) 
                        FROM TRANSAC,DEBT,PAYMENT 
                            WHERE TRANSAC.ID=DEBT.TR_REF AND 
                            TRANSAC.CREATED_BY=%s AND 
                            (debt.id=PAYMENT.debt_ref OR (SELECT COUNT(*) FROM PAYMENT WHERE DEBT_REF=DEBT.ID)=0) 
                                group by debt.id,transac.id ORDER BY ID(debt)"""
        elif id:
            query = """SELECT * FROM DEBT WHERE ID=%s"""
        else:
            query = """SELECT * FROM TRANSAC,DEBT WHERE TRANSAC.ID=DEBT.TR_REF ORDER BY ID(DEBT)"""


        try:
            if webuser_id:
                cursor.execute(query, (webuser_id,))
            elif id:
                cursor.execute(query, (id,))
                debt = cursor.fetchone()
                return models.Debt(debt)
            else:
                cursor.execute(query, tuple())
            debts_and_transacs = cursor.fetchall()
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    for debt_and_transac in debts_and_transacs:
        tr = debt_and_transac[:7]
        debt = debt_and_transac[7:]
        debt_obj = models.Debt(debt)
        debt_list.append(debt_obj)

    return debt_list

def get_transaction(ID):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM TRANSAC WHERE ID = %s  ORDER BY ID"""
        try:
            cursor.execute(query, (ID,))
            tr = cursor.fetchone()
            if tr:
                tr_obj = (models.Transaction(tr))
            else:
                tr_obj = None
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return tr_obj

def update_tr(tr_obj,confirm_admin_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """UPDATE TRANSAC SET CONFIRMED_BY=%s WHERE ID=%s;"""
        try:
            cursor.execute(query,(confirm_admin_id,tr_obj.id,))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

def insert_payment(transaction_id,debt_id):
    url2 = current_app.config["database_url"]
    query = "INSERT INTO PAYMENT (DEBT_REF, TR_REF) VALUES (%s, %s) returning id "
    with dbapi2.connect(url2) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, (debt_id,transaction_id))
                id = cursor.fetchone()[0]
            except dbapi2.DatabaseError as err:
                print("Warning: ", err)
                pass
    return id

def get_debts_unfinish(webuser_id=None):
    debts = []
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        
        if webuser_id:
            query = """SELECT * from debt where TR_REF in 
                        (SELECT id FROM transac WHERE 
                            (ID IN 
                                (SELECT TR_REF FROM DEBT where number_pay!=paid)) AND
                                (confirmed_by is not NULL) AND
                                (created_by=%s))"""
        else:
            query = """SELECT * from debt where TR_REF in 
                        (SELECT id FROM transac WHERE 
                            (ID IN 
                                (SELECT TR_REF FROM DEBT where number_pay!=paid)) AND
                                (confirmed_by is not NULL))"""

        try:
            if webuser_id:
                cursor.execute(query, (webuser_id,))
            else:
                cursor.execute(query)
            trs = cursor.fetchall()

            for tr in trs:
                debts.append(models.Debt(tr))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return debts

def payment_count():
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        
        query = """SELECT count(*) FROM PAYMENT"""
       
        try:
            cursor.execute(query, tuple())
            count = cursor.fetchone()[0]
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass
    return count


def get_payments(webuser_id=None,id=None):
    pay_list = []
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        if webuser_id:
            query = """SELECT * FROM TRANSAC,PAYMENT WHERE TRANSAC.ID=PAYMENT.TR_REF AND TRANSAC.CREATED_BY=%s ORDER BY ID(TRANSAC)"""
        elif id:
            query = """SELECT * FROM PAYMENT WHERE ID=%s ORDER BY ID """
        else:
            query = """SELECT * FROM TRANSAC,PAYMENT WHERE TRANSAC.ID=PAYMENT.TR_REF ORDER BY ID(TRANSAC)"""

        try:
            if webuser_id:
                cursor.execute(query, (webuser_id,))
            elif id:
                cursor.execute(query, (id,))
                pay_ = cursor.fetchone()
                return models.Payment(pay_)
            else:
                cursor.execute(query, tuple())
            pays_and_transacs = cursor.fetchall()
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    for pay_and_transac in pays_and_transacs:
        tr = pay_and_transac[:7]
        pay = pay_and_transac[7:]
        pay_obj = models.Payment(pay)
        pay_list.append(pay_obj)

    return pay_list

def is_payement(tr_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM PAYMENT WHERE %s=PAYMENT.TR_REF ORDER BY ID"""

        try:
            cursor.execute(query, (tr_id,))
            pay = cursor.fetchone()
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass
    if pay:
        return models.Payment(pay)
    else:
        return 0

def payment_confirm(pay_obj):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        pay_obj.debt_ref.paid+=1
        pay_obj.debt_ref.amount_pay+=pay_obj.tr_ref.amount
        pay_obj.pay_num = pay_obj.debt_ref.paid
        query_pay = """UPDATE PAYMENT SET PAY_NUM=%s WHERE ID=%s;"""
        query_debt = """UPDATE DEBT SET PAID=%s,AMOUNT_PAY=%s WHERE ID=%s;"""
        try:
            cursor.execute(query_pay,(pay_obj.pay_num,pay_obj.id))
            cursor.execute(query_debt,(pay_obj.debt_ref.paid,pay_obj.debt_ref.amount_pay,pay_obj.debt_ref.id))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

def get_address(ID):
    if ID==None:
        return None
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM ADDRESS WHERE ID = %s  ORDER BY ID"""
        try:
            cursor.execute(query, (ID,))
            addr = cursor.fetchone()
            if addr:
                addr_obj = (models.Address(addr))
            else:
                addr_obj = None
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

    return addr_obj

def update_address(form,addr_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """UPDATE ADDRESS SET ADDRESS_NAME=%s,COUNTRY=%s,CITY=%s,DISTRICT=%s,NEIGHBORHOOD=%s,AVENUE=%s,STREET=%s,ADDR_NUMBER=%s,ZIPCODE=%s,EXPLANATION=%s WHERE ID=%s;"""
        print((form.address_name.data,form.country.data,form.city.data,form.district.data,form.neighborhood.data,form.avenue.data,form.street.data,form.addr_number.data,form.zipcode.data,form.explanation.data,addr_id))
        try:
            cursor.execute(query,(form.address_name.data,form.country.data,form.city.data,form.district.data,form.neighborhood.data,form.avenue.data,form.street.data,form.addr_number.data,form.zipcode.data,form.explanation.data,addr_id))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

def insert_address(form):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO ADDRESS (ADDRESS_NAME,COUNTRY,CITY,DISTRICT,NEIGHBORHOOD,AVENUE,STREET,ADDR_NUMBER,ZIPCODE,EXPLANATION) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id"""
        try:
            cursor.execute(query,(form.address_name.data,form.country.data,form.city.data,form.district.data,form.neighborhood.data,form.avenue.data,form.street.data,form.addr_number.data,form.zipcode.data,form.explanation.data))
            addr_id = cursor.fetchone()[0]
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass
    return addr_id

def update_admin(admin_obj):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """UPDATE ADMIN SET PHONE_NUM=%s,ADMIN_PASSWORD=%s,ADDRESS_REF=%s WHERE ID=%s;"""
        try:
            cursor.execute(query,(admin_obj.phone_num,admin_obj.admin_password,admin_obj.address_ref.id,admin_obj.id))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

def delete_address(addr_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """DELETE FROM ADDRESS WHERE ID=%s;"""
        try:
            cursor.execute(query,(addr_id,))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

def remove_debt(debt_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """DELETE FROM payment WHERE payment.debt_ref=%s; DELETE FROM debt WHERE ID=%s;"""
        try:
            cursor.execute(query,(debt_id,debt_id))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass

def remove_webuser(webuser_id):
    with dbapi2.connect(current_app.config["database_url"]) as connection:
        cursor = connection.cursor()
        query = """DELETE FROM webuser WHERE id=%s;"""
        try:
            cursor.execute(query,(webuser_id,))
        except dbapi2.DatabaseError as err:
            print("Warning: ", err)
            pass