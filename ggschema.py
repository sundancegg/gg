from marshmallow import Schema, fields, ValidationError
import uuid
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()

# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
tx_id = uuid.uuid1()


class GGReview(Schema):
    rating = fields.Integer()
    review = fields.Str()
    src_addr = fields.Str() # who wrote it
    dst_addr = fields.Str() # who is it about
    transaction_id = fields.Str()


class GGPrivateSession(Schema):
    date = fields.DateTime
    temple = fields.String()
    goddess = GGReview
    patron = GGReview
    donation = fields.Integer()


class GGGoddess(Schema):
    # Goddess Guild
    name = fields.String()
    rating = fields.Integer()
    profile_link = fields.String()
    division = fields.Integer()
    pending_review_lock = fields.Integer()
    temples = fields.List(fields.String)
    review_links = fields.List(fields.String)
    contract_addr = fields.Str()

    # TODO:
    # temple_badges
    # skill_badges
    # completed_sessions: int128 ...? needed?


class GGPatron(Schema):
    name = fields.String()
    rating = fields.Integer()
    profile_link = fields.String()
    division = fields.Integer()
    pending_review_lock = fields.Integer()
    temples = fields.List(fields.String)
    review_links = fields.List(fields.String)
    contract_addr = fields.Str()


test_review_patron = {
    "rating": 5,
    "review": "them hoes bustin",
    "src_addr": "0x11patron11",
    "dst_addr": "0x00goddess00",
    "transaction_id": tx_id
}

test_review_goddess = {
    "rating": 5,
    "review": "he was a devil but i kinda liked it",
    "src_addr": "0x00goddess00",
    "dst_addr": "0x11patron11",
    "transaction_id": "tx_id"
}

test_session = {
    "date": dt_string,
    "temple": "0xtempleID1924",
    "goddess": test_review_goddess,
    "patron": test_review_patron,
    "donation": 123,
    "transaction_id": tx_id
}