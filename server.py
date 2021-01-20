from flask import Flask, render_template,redirect, url_for, flash, request, abort
from flask_login import UserMixin,LoginManager,login_user,login_required, logout_user, current_user
from forms import *
import os
import db
from passlib.handlers.pbkdf2 import pbkdf2_sha256 as hasher
from authorization import admin_required, member_required
from datetime import datetime
import utils

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["database_url"] = os.getenv("DATABASE_URL")
app.debug=True
lm = LoginManager()

class FlaskUser(UserMixin):
    def __init__(self, email,is_active,ID):
        self.username = email
        self.is_active_ = is_active
        self.id = ID
        if db.get_admin(webuser_id=ID):
            self.is_admin = True
            self.admin = db.get_admin(webuser_id=ID)
        else:
            self.is_admin = False
        if db.get_member(ID):
            self.is_member = True
        else:
            self.is_member = False

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.is_active_

@lm.user_loader
def load_user(ID):
    webuser_obj = db.get_webuser(id=ID)
    return FlaskUser(email=webuser_obj.email,is_active=webuser_obj.is_active,ID=webuser_obj.id)

lm.init_app(app)
lm.login_view = "signin_page"
lm.login_message = "giriş yapınız"
lm.login_message_category = 'danger'

@app.route("/")
@login_required
def home_page():
    return render_template("layout.html")

@app.route("/index")
@login_required
def index_page():
    if current_user.is_admin or current_user.is_member:
        return render_template("index.html")
    else:
        flash("Üyeliğiniz onay beklemektedir","danger")
        return redirect(url_for("home_page"))


@app.route("/signup",methods=["POST","GET"])
def signup_page():
    form = SignupForm()
    if form.validate_on_submit():
        password_hash = hasher.hash(form.password.data)
        webuser_obj = db.get_webuser(email=form.email.data)
        if webuser_obj:
            flash("This email already registered","danger")
        else:
            db.insert(PASSWORD_HASH=password_hash, EMAIL=form.email.data, NAME=form.name.data, SURNAME=form.surname.data)
            return redirect(url_for("signin_page"))
    return render_template("forms.html",form=FormInfo("Signup",form))

@app.route("/member_edit",methods=["POST","GET"])
@login_required
def member_edit():
    form = SignupForm()
    webuser_obj = db.get_webuser(id=current_user.id)
    if form.validate_on_submit():
        password_hash = hasher.hash(form.password.data)
        if webuser_obj:
            db.update(password_hash=password_hash, email=form.email.data, name=form.name.data, surname=form.surname.data)
            flash("Bilgiler güncellendi","success")
            return redirect(url_for("home_page"))
    print()
    form.email.data = webuser_obj.email
    form.name.data = webuser_obj.name
    form.surname.data = webuser_obj.surname

    form.email.render_kw["readonly"]=""

    return render_template("forms.html",form=FormInfo("Signup",form))

@app.route("/signin",methods=["POST","GET"])
def signin_page():
    form = SigninForm()
    if form.validate_on_submit():        
        webuser_obj = db.get_webuser(email=form.email.data)
        if webuser_obj:
            if hasher.verify(form.password.data, webuser_obj.password_hash):
                login_user(FlaskUser(email=webuser_obj.email,is_active=webuser_obj.is_active,ID=webuser_obj.id),remember=form.remember.data)
                next_page = request.args.get("next", url_for("home_page"))
                flash("Logged in succesfully","success")
                return redirect(next_page)
            else:                
                flash("Password is wrong","danger")
        else:            
            flash("This email not registered","danger")
    return render_template("forms.html",form=FormInfo("Signin",form))


@app.route("/logout",methods=["POST","GET"])
def logout_page():
    logout_user()
    flash("Logged out succesfully","danger")
    return redirect(url_for("home_page"))


@app.route("/confirm",methods=["POST","GET"])
@admin_required
def confirm_page():
    webusers_obj = db.get_webusers_unconfirmed()
    return render_template("confirm.html",members=webusers_obj)

@app.route("/confirm/<int:id>",methods=["POST","GET"])
@admin_required
def confirm_member_page(id):    
    if db.get_member(id):
        flash("This user already confirmed","danger")
    else:
        admin_obj = db.get_admin(webuser_id=current_user.id)
        db.insert_member(admin_obj.id,id)

    return redirect(url_for("confirm_page"))

@app.route("/member_views",methods=["POST","GET"])
@member_required
def member_views():
    debt_list = db.get_debts(current_user.id)
    pay_list = db.get_payments(current_user.id)
    return render_template("member_view.html",debts=debt_list,pays=pay_list)

@app.route("/transaction",methods=["POST","GET"])
@member_required
def make_debt():    
    form = DebtForm()
    if form.validate_on_submit():        
        id = db.insert_transaction(form.amount.data,current_user.id)
        current_month = datetime.now().month
        current_year = datetime.now().year
        start_datetime = utils.date_calculator(current_month,current_year,form.start_period.data)
        due_datetime = utils.date_calculator(current_month,current_year,form.start_period.data+form.number_pay.data-1)
        db.insert_debt(id,due_datetime,start_datetime,form.number_pay.data)
        return redirect(url_for("member_views"))
    return render_template("forms.html",form=FormInfo("Add Debts",form))

@app.route("/all_tr",methods=["POST","GET"])
@admin_required
def all_tr():
    debts_obj = db.get_debts()
    payment_obj = db.get_payments()
    for debt in debts_obj:
        print("debt.tr_ref.confirmed_by: ",debt.tr_ref.confirmed_by)
    return render_template("member_view.html",debts=debts_obj,pays=payment_obj)

@app.route("/confirm_tr/<int:id>",methods=["POST","GET"])
@admin_required
def confirm_tr_page(id):
    tr_obj = db.get_transaction(id)   
    if tr_obj:
        current_admin = db.get_admin(webuser_id=current_user.id)
        db.update_tr(tr_obj,current_admin.id)
    else:
        abort(404)

    pay_obj = db.is_payement(id)
    if pay_obj:
        db.payment_confirm(pay_obj)
    return redirect(url_for("all_tr"))

@app.route("/tr_admin",methods=["POST","GET"])
@admin_required
def tr_admin():
    members = [(member.webuser_ref.id,member.webuser_ref.name + " " + member.webuser_ref.surname) for member in db.get_members()]
    form = DebtAdminForm(member_list=members)
    if form.validate_on_submit():
        id = db.insert_transaction(form.amount.data,form.member.data)
        current_month = datetime.now().month
        current_year = datetime.now().year
        start_datetime = utils.date_calculator(current_month,current_year,form.start_period.data)
        due_datetime = utils.date_calculator(current_month,current_year,form.start_period.data+form.number_pay.data-1)
        db.insert_debt(id,due_datetime,start_datetime,form.number_pay.data)
        return redirect(url_for("all_tr"))
    return render_template("forms.html",form=FormInfo("Add Debts From Admin",form))


@app.route("/payement",methods=["POST","GET"])
@member_required
def payment_member():
    debts = [(debt.id) for debt in db.get_debts_unfinish(webuser_id=current_user.id)]
    # debts = db.get_debts_unfinish(current_user.id
    form = PayementForm(debt_list=debts)
    if form.validate_on_submit():
        id = db.insert_transaction(form.amount.data,current_user.id)
        debt_ = db.get_debts(id=form.debt_ref.data)
        db.insert_payment(transaction_id=id,debt_id=form.debt_ref.data)

    return render_template("forms.html",form=FormInfo("Add Payement From Member",form))


@app.route("/confirm_pay/<int:id>",methods=["POST","GET"])
@admin_required
def confirm_pay_page(id):
    payment_obj = db.get_payments(id=id)
    return render_template("confirm.html",members=payment_obj)

@app.route("/edit_address",methods=["POST","GET"])
@admin_required
def edit_address():
    form = AddressForm()
    if form.validate_on_submit():
        print("asd")
        if current_user.admin.address_ref:
            print(form)
            db.update_address(form,current_user.admin.address_ref.id)
        else:
            adrr_id = db.insert_address(form)
            current_user.admin.address_ref = db.get_address(adrr_id)
            db.update_admin(current_user.admin)

    if current_user.admin.address_ref:
        address = db.get_address(current_user.admin.address_ref.id)
        form.address_name.data = address.address_name
        form.country.data = address.country
        form.city.data = address.city
        form.district.data = address.district
        form.neighborhood.data = address.neighborhood
        form.avenue.data = address.avenue
        form.street.data = address.street
        form.addr_number.data = address.addr_number
        form.zipcode.data = address.zipcode
        form.explanation.data = address.explanation

    return render_template("forms.html",form=FormInfo("Update Address",form))

@app.route("/remove_address",methods=["POST","GET"])
@admin_required
def remove_address():
    if current_user.admin.address_ref:
        current_user.admin.address_ref.id=None
        db.update_admin(current_user.admin)
        db.delete_address(current_user.admin.address_ref.id)
        flash("address silindi","success")
        current_user.admin.address_ref = None
    else:
        flash("address zaten yok", "danger")

    return redirect(url_for("index_page"))

@app.route("/remove_debt/<int:debt_id>",methods=["POST","GET"])
@admin_required
def remove_debt(debt_id):
    db.remove_debt(debt_id)
    return redirect(url_for("all_tr"))

@app.route("/remove_webuser/<int:webuser_id>",methods=["POST","GET"])
@admin_required
def remove_webuser(webuser_id):
    db.remove_webuser(webuser_id)
    return redirect(url_for("confirm_page"))

if __name__ == "__main__":
    app.run(debug=True)
