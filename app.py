#app.py file where is the flask application for the website deployment
#Developed by Cuitlahuac Daniel Maldonado Ruiz

#Import dependencies
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/uploader", methods = ["GET", "POST"])
def upload_files():
    if request.method == "POST":
        f = request.files["file1"]
        f.save(secure_filename(f.filename))
        return "File uploaded successfully"

if __name__ == "__main__":
    app.run(debug=True)