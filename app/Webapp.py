from flask import Flask 

app = Flask(__name__)

@app.route("/")
def index():
  return {"test": "hello-world"}

if __name__ == "__main__":
  app.run(
    host= "0.0.0.0"
    ,port= 8989
    ,debug= True
  )