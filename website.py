pip install flask requests sqlalchemy    // install packages


from flask import Flask, request, redirect, url_for, render_template
from models import db, Stock
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'  # Replace with your Alpha Vantage API key

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    stocks = Stock.query.all()
    return render_template('index.html', stocks=stocks)

@app.route('/add', methods=['POST'])
def add_stock():
    symbol = request.form.get('symbol')
    if symbol:
        # Fetch stock data
        response = requests.get(f'https://www.alphavantage.co/query', params={
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        })
        data = response.json()
        if 'Time Series (Daily)' in data:
            stock = Stock(symbol=symbol, name=data['Meta Data']['2. Symbol'])
            db.session.add(stock)
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/remove/<int:stock_id>', methods=['POST'])
def remove_stock(stock_id):
    stock = Stock.query.get(stock_id)
    if stock:
        db.session.delete(stock)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Portfolio Tracker</title>
</head>
<body>
    <h1>Stock Portfolio Tracker</h1>
    <form action="/add" method="post">
        <input type="text" name="symbol" placeholder="Enter Stock Symbol" required>
        <button type="submit">Add Stock</button>
    </form>
    <h2>Your Portfolio</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for stock in stocks %}
            <tr>
                <td>{{ stock.symbol }}</td>
                <td>{{ stock.name }}</td>
                <td>
                    <form action="/remove/{{ stock.id }}" method="post">
                        <button type="submit">Remove</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
