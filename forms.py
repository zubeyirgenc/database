from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import InputRequired, Length, Email


def form_open(form_name, id=None, enctype=None):
    open = """<form action="" method="post" name="%s" """ % (form_name)

    if id:
        open += """ id="%s" """ % (id)
    if enctype:
        open += """ enctype="%s" """ % (enctype)

    open += """class="moneytrade-form">"""
    return open

class SignupForm(FlaskForm):
    name = StringField(label="Name",validators=[Length(max=50,message="Geçerli bir isim giriniz"),InputRequired("İsim zorunludur")],id="name",render_kw={"placeholder": "name", "class": "form-control"})
    surname = StringField(label="Surname",validators=[Length(max=50,message="Geçerli bir soyisim giriniz"),InputRequired("Soyisim gereklidir")],id="surname",render_kw={"placeholder": "surname", "class": "form-control"})
    email = EmailField(label="Email",validators=[Length(max=50,message="Geçerli bir email giriniz"),Email("Geçerli bir email giriniz"),InputRequired("Email gereklidir")],id="email",render_kw={"placeholder": "email", "class": "form-control"})
    password = PasswordField(label="Password",validators=[Length(max=50,message="Geçerli bir parola giriniz"),InputRequired("Parola gereklidir")],id="password",render_kw={"placeholder": "email", "class": "form-control"})
    open = form_open(form_name='webuser-form')
    close = """</form>"""
    submit = SubmitField("Basınız", render_kw={"class": "btn btn-primary moneytrade-btn-form"})

class SigninForm(FlaskForm):
    email = EmailField(label="Email",validators=[Length(max=50,message="Geçerli bir email giriniz"),Email("Geçerli bir email giriniz"),InputRequired("Email gereklidir")],id="email",render_kw={"placeholder": "email", "class": "form-control"})
    password = PasswordField(label="Password",validators=[Length(max=50,message="Geçerli bir password giriniz"),InputRequired("Parola gereklidir")],id="password",render_kw={"placeholder": "password", "class": "form-control"})
    remember = BooleanField(label="Beni Hatırla")
    open = form_open(form_name='webuser-form')
    close = """</form>"""
    submit = SubmitField("Gönder", render_kw={"class": "btn btn-primary moneytrade-btn-form"})

class DebtAdminForm(FlaskForm):
    member = SelectField(
        label="Kişi", validators=[InputRequired("Kişi seçiniz")],choices=[], id='member', coerce=int,
        render_kw={"class": "form-control"}
    )
    amount = IntegerField(label="Amount",validators=[InputRequired("Geçerli amount giriniz")],id="amount",render_kw={"placeholder": "0", "class": "form-control"})  
    start_period = IntegerField(label="Kaç ay sonra",validators=[InputRequired("Geçerli bir start_period giriniz")],id="start_period",render_kw={"placeholder": "0", "class": "form-control"})
    number_pay = IntegerField(label="Taksit sayısı",validators=[InputRequired("Geçerli bir number_pay giriniz")],id="number_pay",render_kw={"placeholder": "0", "class": "form-control"})
    submit = SubmitField("Basınız", render_kw={"class": "btn btn-primary moneytrade-btn-form"})
    open = form_open(form_name='debt-form')
    close = """</form>"""

    def __init__(self, member_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if member_list:
            self.member.choices=member_list
        else:
            self.member = None

class DebtForm(FlaskForm):
    amount = IntegerField(label="Amount",validators=[InputRequired("Geçerli amount giriniz")],id="amount",render_kw={"placeholder": "0", "class": "form-control"})  
    start_period = IntegerField(label="Kaç ay sonra",validators=[InputRequired("Geçerli bir start_period giriniz")],id="start_period",render_kw={"placeholder": "0", "class": "form-control"})
    number_pay = IntegerField(label="Taksit sayısı",validators=[InputRequired("Geçerli bir number_pay giriniz")],id="number_pay",render_kw={"placeholder": "0", "class": "form-control"})
    submit = SubmitField("Basınız", render_kw={"class": "btn btn-primary moneytrade-btn-form"})
    open = form_open(form_name='debt-form')
    close = """</form>"""

class PayementForm(FlaskForm):
    debt_ref = SelectField(
        label="Hangi Borca Ait", validators=[],choices=[], id='debt_ref', coerce=int,
        render_kw={"class": "form-control"}
    )
    amount = IntegerField(label="Amount",validators=[InputRequired("Geçerli amount giriniz")],id="amount",render_kw={"placeholder": "0", "class": "form-control"})
    submit = SubmitField("Basınız", render_kw={"class": "btn btn-primary moneytrade-btn-form"})
    open = form_open(form_name='payment-form')
    close = """</form>"""

    def __init__(self, debt_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if debt_list:
            print("debt_list: ",debt_list)
            self.debt_ref.choices=debt_list
        else:
            self.debt_ref = None

class AddressForm(FlaskForm):
    address_name = StringField(label="address_name",validators=[Length(max=30,message="Geçerli uzunlukta bir address_name giriniz")],render_kw={"class": "form-control"})
    country = StringField(label="country",validators=[Length(max=30,message="Geçerli uzunlukta bir country giriniz"),InputRequired("İsim zorunludur")],render_kw={"class": "form-control"})
    city = StringField(label="city",validators=[Length(max=30,message="Geçerli uzunlukta bir city giriniz"),InputRequired("İsim zorunludur")],render_kw={"class": "form-control"})
    district = StringField(label="district",validators=[Length(max=30,message="Geçerli uzunlukta bir district giriniz")],render_kw={"class": "form-control"})
    neighborhood = StringField(label="neighborhood",validators=[Length(max=30,message="Geçerli uzunlukta bir neighborhood giriniz")],render_kw={"class": "form-control"})
    avenue = StringField(label="avenue",validators=[Length(max=30,message="Geçerli uzunlukta bir avenue giriniz")],render_kw={"class": "form-control"})
    street = StringField(label="street",validators=[Length(max=30,message="Geçerli uzunlukta bir street giriniz")],render_kw={"class": "form-control"})
    addr_number = StringField(label="addr_number",validators=[Length(max=10,message="Geçerli uzunlukta bir addr_number giriniz")],render_kw={"class": "form-control"})
    zipcode = StringField(label="zipcode",validators=[Length(max=5,message="Geçerli uzunlukta bir zipcode giriniz")],render_kw={"class": "form-control"})
    explanation = TextAreaField(label="explanation",validators=[Length(max=500,message="Geçerli uzunlukta bir explanation giriniz")],render_kw={"class": "form-control"})
    open = form_open(form_name='address-form')
    close = """</form>"""
    submit = SubmitField("Basınız", render_kw={"class": "btn btn-primary moneytrade-btn-form"})

class FormInfo:

    def __init__(self, title, form):
        self.title = title
        self.form = form
        self.errors = []

        for field in form:
            self.errors += field.errors