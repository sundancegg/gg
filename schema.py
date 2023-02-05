from marshmallow import Schema, fields, ValidationError

def check_gender(data):
    valid_list = ["male", "female"]
    if data not in valid_list:
        raise ValidationError(
            'Invalid gender. Valid choices are'+ valid_list
        )

class SchemaGoddess(Schema):
    # Goddess Guild
    goddess_name: fields.String()
    avg_rating: fields.Integer()
    profile_link: fields.String()
    goddess_division: fields.Integer()
    review_links: fields.List(fields.String)

    # TODO:
    # temple_badges
    # skill_badges
    # completed_sessions: int128 ...? needed?
