#!/usr/local/bin/python3

import os
import w3storage
import json
from dotenv import load_dotenv
from web3 import Web3, Account, HTTPProvider
from flask import Flask, render_template, request, jsonify
from web3.middleware import geth_poa_middleware
from interactive import read_contract_var, write_contract_var, deploy_patron_contract, deploy_goddess_contract, read_temple_var
import random
from eth_account.messages import defunct_hash_message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, set_access_cookies
import string
from ggschema import GGReview, GGPatron, GGGoddess

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
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
jwt = JWTManager(app)

# TODO: get rid of this
# Our running user db {wallet_addr: nonce}
USERS_NONCE_DB = {}

@app.route("/")
def index():
    # goddess_name = read_contract_var(w3, "goddess", "goddess_name")
    # rating = read_contract_var(w3, "goddess", "rating")
    # profile_link = read_contract_var(w3, "goddess", "profile_link")
    # goddess_division = read_contract_var(w3, "goddess", "goddess_division")

    return render_template("metamask.html") 

    #return render_template("index.html", goddess_name=goddess_name, 
     #   rating=rating, profile_link=profile_link, goddess_division=goddess_division)


# Updates goddess contract
# @app.route("/patron/<addr>" , methods=['GET'])
# def patron(addr):
#     data = {
#         "patron_name": read_contract_var(w3, "patron", "patron_name"),
#         "rating": read_contract_var(w3, "patron", "rating"),
#         "profile_link": read_contract_var(w3, "patron", "profile_link"),
#         "division": read_contract_var(w3, "patron", "division"),
#         "pending_review_lock": read_contract_var(w3, "patron", "pending_review_lock"),
#         "temples": read_contract_var(w3, "patron", "temples"),
#         "review_links": read_contract_var(w3, "patron", "get_review_links")}

#     return data, 200  


@app.route("/join-temple-goddess/<temple>/<goddess>" , methods=['GET'])
def join_temple_goddess(temple, goddess):
    pass


@app.route("/join-temple-patron/<temple>/<patron>" , methods=['GET'])
def join_temple_patron(temple, patron):
    write_contract_var(w3, "patron", "join_temple", os.getenv('CONTRACT_ADDRESS_TEMPLE'))  
    temples = read_contract_var(w3, "patron", "get_temples")

    return temples, 200    


@app.route("/temple/<addr>" , methods=['POST'])
def get_temple(addr):
    data = {
        "name": read_temple_var(w3, addr, "TempleName"), 
        "base_rate": read_temple_var(w3, addr, "BaseRate"), 
        "patrons": read_temple_var(w3, addr, "get_patrons"),
        "goddesses": read_temple_var(w3, addr, "get_goddesses"),
    }

    return data, 200


@app.route("/patron/<addr>" , methods=['GET'])
def patron(addr):
    data = {
        "name": read_contract_var(w3, "patron", "name"),
        "division": read_contract_var(w3, "patron", "division"),
        "review_links": read_contract_var(w3, "patron", "get_review_links"),
        "temples": read_contract_var(w3, "patron", "get_temples")
    }

    # Sanitize inputs
    gg_patron = GGPatron().load(data)
    print(gg_patron)

    return render_template("patron.html", gg_patron=gg_patron, addr=addr)


@app.route("/patron" , methods=['POST'])
def post_patron():
    # TODO:: sign the review for security
    data = {
        "name": request.form.get("name"),
        "division": request.form.get("division"),
        "profile_link": request.form.get("profile_link"),
        "temples":  [request.form.get("temple")],
        #"review_links":  request.form.get("review_links")
    }

    # Sanitize inputs
    gg_patron = GGPatron().load(data)

    gg_patron['contract_addr'] = deploy_patron_contract(
            w3, gg_patron['name'], gg_patron['profile_link'], 
            gg_patron['division'], gg_patron['temples'][0])

    return gg_patron, 200  


@app.route('/secret')
@jwt_required()
def secret():
  return (f"HELLO to our secret page: {get_jwt_identity()}")


# Updates goddess contract
@app.route("/deploy-profile" , methods=['POST'])
def deploy_profile():
    pass


@app.route("/goddess" , methods=['POST'])
def post_goddess():
    # TODO:: sign the review for security
    data = {
        "name": request.form.get("name"),
        "profile_link": request.form.get("profile_link"),
        "temples":  [request.form.get("temple")],
    }

    # Sanitize inputs
    gg_goddess = GGGoddess().load(data)
    gg_goddess['contract_addr'] = deploy_goddess_contract(
            w3, gg_goddess['name'], gg_goddess['profile_link'], 
            gg_goddess['temples'][0])

    return gg_goddess, 200  


# Updates goddess contract
@app.route("/get-reviews/<user_profile_addr>", methods=['GET']) # change this
def get_reviews(user_profile_addr):
    base = os.getenv('WEB3_STORAGE_VIEW_BASE')

    # update contracts with link
    links = read_contract_var(w3, user_profile_addr, "get_review_links")
    full_links = [os.getenv('WEB3_STORAGE_VIEW_BASE') + x for x in links]    
    return full_links, 200


# Updates goddess contract
@app.route("/set-review", methods=['POST']) # change this
def set_review():
    
    # TODO:: sign the review for security
    data = {
        "rating": request.form.get("rating"),
        "review": request.form.get("review"),
        "src_addr": request.form.get("src_addr"),
        "dst_addr": request.form.get("dst_addr"),
        "transaction_id":  request.form.get("transaction_id")
    }

    # TODO:: Sanitize inputs
    gg_review = GGReview().load(data)

    # Store on ipfs
    review_cid = w3s.post_upload(("test1", json.dumps(gg_review), 'application/json'))

    # update contracts with link
    write_contract_var(w3, "goddess", "add_review_link", review_cid)    

    gg_review['review_cid'] = os.getenv('WEB3_STORAGE_VIEW_BASE') + review_cid
    # return render_template("review.html", gg_review=gg_review) 
    return gg_review, 200


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


