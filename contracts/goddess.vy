# @version ^0.3.7

from . temple import GGSession

# Goddess Guild
goddess_name: public(String[200])
rating: public(int128)
profile_link: public(String[100])
goddess_division: public(int128)
pending_review_lock: public(String[100]) # must write a review about last session before next

# TODO: This is obvs broken and bad design :(
review_links: public(DynArray[String[222], 128])

# TODO:
# temple_badges
# skill_badges


@external
def get_review_links() -> DynArray[String[222], 128]:
    return self.review_links

   
@external
def update_goddess_name(_goddess_name: String[200]):
    self.goddess_name = _goddess_name


@external
def update_profile_link(_profile_link: String[100]):
    self.profile_link = _profile_link


@external
def add_review_link(_link: String[222]):
    assert (len(self.review_links) < 128) # TODO: fix this
    self.review_links.append(_link)


@external
def update_goddess_division(_goddess_division: int128):
    assert (_goddess_division > 0)
    assert (_goddess_division <= 3)
    self.goddess_division = _goddess_division