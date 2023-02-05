import os
import w3storage
import json
from dotenv import load_dotenv
from web3 import Web3, Account, HTTPProvider
from flask import Flask, render_template, request, jsonify
from web3.middleware import geth_poa_middleware
from interactive import read_contract_var, write_contract_var
import random
from eth_account.messages import defunct_hash_message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, set_access_cookies
import string

# load environment variables from .env file
load_dotenv('.env')

# web3.py instance
w3 = Web3(HTTPProvider(os.getenv('RPC_URL')))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
acct = w3.eth.account.privateKeyToAccount(os.getenv('PRIVATE_KEY'))
assert(w3.isConnected())

# storage
w3s = w3storage.API(token=os.getenv('WEB3_STORAGE_KEY'))

# account setup
private_key= os.environ.get('PRIVATE_KEY') #private key of the account
public_key = Account.from_key(private_key)
account_address = public_key.address

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = ''.join(random.choice(string.ascii_lowercase) for i in range(22))
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True
#app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
jwt = JWTManager(app)

# TODO: get rid of this
# Our running user db {wallet_addr: nonce}
USERS_NONCE_DB = {}

@app.route("/")
def index():
    goddess_name = read_contract_var(w3, "goddess", "goddess_name")
    avg_rating = read_contract_var(w3, "goddess", "avg_rating")
    profile_link = read_contract_var(w3, "goddess", "profile_link")
    goddess_division = read_contract_var(w3, "goddess", "goddess_division")

    return render_template("metamask.html") 

    #return render_template("index.html", goddess_name=goddess_name, 
     #   avg_rating=avg_rating, profile_link=profile_link, goddess_division=goddess_division)

@app.route('/secret')
@jwt_required()
def secret():
  return (f"HELLO to our secret page: {get_jwt_identity()}")

# Updates goddess contract
@app.route("/setGoddess" , methods=['POST'])
def set_goddess():
    goddess_name = request.form.get("goddess_name")
    avg_rating = request.form.get("avg_rating")
    profile_link = request.form.get("profile_link")
    goddess_division = request.form.get("goddess_division")

    write_contract_var(w3, "goddess", "update_goddess_name", goddess_name)
    write_contract_var(w3, "goddess", "update_profile_link", profile_link)

    return render_template("index.html", goddess_name=goddess_name, 
        avg_rating=avg_rating, profile_link=profile_link, goddess_division=goddess_division)


# Updates goddess contract
@app.route("/setReview", methods=['POST', 'GET']) # change this
def set_review():
    rating = 'none'
    review = 'none'
    review_cid = 'none'

    # Fix this
    if request.method == 'POST':
        rating = request.form.get("rating")
        review = request.form.get("review")
        
        # Store on ipfs
        review_cid = w3s.post_upload((f"Rating: {rating}\nReview: {review}"))

        # update contracts with link
        write_contract_var(w3, "goddess", "add_review_link", review_cid)    

    return render_template("review.html", rating=rating, review=review, 
        review_link=review_cid) 


# Updates goddess contract
@app.route("/auth/<wallet_addr>", methods=['POST', 'GET']) # change this
def auth(wallet_addr):
    hash_msg = "Hello wallet {}, your nonce is: {}"

    if request.method == 'GET':
        nonce = random.randint(0, 9999)
        USERS_NONCE_DB[wallet_addr] = nonce
        msg = hash_msg.format(wallet_addr, nonce)
        return {"token_phrase": msg}

    if request.method == 'POST':
        signature = request.json['signature']
        original_message = hash_msg.format(wallet_addr, USERS_NONCE_DB[wallet_addr])
        message_hash = defunct_hash_message(text=original_message)
        signer = w3.eth.account.recoverHash(message_hash, signature=signature)

        if signer.lower() != wallet_addr:
            return 'could not authenticate signature', 401
            
        access_token = create_access_token(identity=wallet_addr)

        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        return resp, 200


if __name__ == '__main__':
    app.run(port=8000, host='localhost')


