from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_notifier', methods=['POST'])
def start_notifier():
    phone_number = request.form.get('phone_number')
    stock_symbol = request.form.get('stock_symbol')

    if not phone_number or not stock_symbol:
        return "Phone number and stock symbol are required.", 400

    try:
        subprocess.Popen(["python3", "notifier.py", phone_number, stock_symbol])
        return f"Notifier started for {stock_symbol} to {phone_number}."
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
