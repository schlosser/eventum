from flask import Flask, render_template
from sys import argv

app = Flask(__name__)

# Debug configurations
debug = len(argv) == 2 and argv[1] == "debug"

@app.route('/')
def home():
	return render_template("app.html")

if __name__ == '__main__':
	if debug:
		app.run(debug=True, host="0.0.0.0")
	else:
		app.run()
