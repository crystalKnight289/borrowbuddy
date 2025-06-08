from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    image_url = db.Column(db.String(300))
    status = db.Column(db.String(20))  # 'on_sale' or 'sold'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.drop_all()      # Drop all tables (careful: this deletes existing data)
    db.create_all()    # Recreate tables with new schema

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy')
def buy_page():
    products = Product.query.filter_by(status='on_sale').all()
    return render_template('buy.html', products=products)

@app.route('/sell', methods=['GET', 'POST'])
def sell_page():
    if request.method == 'POST':
        new_product = Product(
            title=request.form['title'],
            description=request.form['description'],
            price=float(request.form['price']),
            image_url=request.form['image_url'],
            status='on_sale'
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('sell_page'))
    return render_template('sell.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return redirect(url_for('index'))
        else:
            message = 'Invalid username or password'
    return render_template('login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            message = 'Passwords do not match.'
        else:
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                message = 'Username or Email already taken. Please choose another.'
            else:
                new_user = User(username=username, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))

    return render_template('signup.html', message=message)

@app.route('/howitworks')
def how_it_works():
    return render_template('howitworks.html')

if __name__ == '__main__':
    app.run(debug=True)