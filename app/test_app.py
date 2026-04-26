from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Krishi Mitr Test Server Running!</h1><p>The Flask server is working correctly.</p>'

if __name__ == '__main__':
    print("Starting Flask test server...")
    print("Visit: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
