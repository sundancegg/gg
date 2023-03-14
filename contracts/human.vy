# @version ^0.3.7

enum divinity_type:
    GODDESS     # 0
    PATRON      # 1

# each session can be in one of these states
enum session_status:
    REQUESTED
    ACCEPTED
    COMPLETED
    CANCELED_PARTNER
    CANCELED_SELF

# details on each session between humans, we store a list of them
struct h_session:
    partner: address # TODO :: contract of your partner
    donation: uint256
    temple: address
    status: session_status

# Wallet owner
owner_wallet_addr: immutable(address)
name: immutable(String[MAX_NAME_LEN])
divinity: immutable(divinity_type)  # Are you a Goddess (0) or Patron (1)

rating: public(uint256)
profile_link: public(String[MAX_LINK_LEN])
division: public(int128)
temples: public(DynArray[address, MAX_TEMPLES])
alter_ego: address # Link to your "other" contract... ie person can switch between goddess & patron

# TODO: This is obvs broken and bad design :(
# This works as a 3 slot storage, so row XX has the the transaction info,
# patron review, and goddess review 
session_reviews_by_self: public(DynArray[String[MAX_LINK_LEN], MAX_REVIEWS]) # This contract is the author of the review
session_reviews_by_partners: public(DynArray[String[MAX_LINK_LEN], MAX_REVIEWS]) # What others said about this contracts owner
session_details: DynArray[h_session, MAX_REVIEWS] # Session details
session_locked: bool # pointer to currently needed review

# TODO:
# temple_badges
# skill_badges

# Interfaces 
# TODO :: import directly
interface Temple:
    def join_temple_patrons() -> bool: payable # TODO :: marker

interface GGHuman:
    def add_review_partner(_rating: uint256, link: String[MAX_LINK_LEN]) -> bool: payable # TODO :: marker

UNLOCKED: constant(int128) = -1
MAX_REVIEWS: constant(int128) = 128
MAX_LINK_LEN: constant(int128) = 200
MAX_TEMPLES: constant(int128) = 50
MAX_NAME_LEN: constant(int128) = 100
EMPTY_ADDR: constant(address) = 0x0000000000000000000000000000000000000000
EMPTY_STR: constant(String[1]) = '\x00'

@external
def __init__(_owner_wallet_addr: address, _name: String[MAX_NAME_LEN], _divinity: divinity_type,
        profile_link: String[MAX_LINK_LEN], division: int128, temple: address):
    # TODO :: add aserts
    owner_wallet_addr = _owner_wallet_addr
    name = _name
    divinity = _divinity
    self.profile_link = profile_link
    self.division = division
    assert(self._join_temple(temple))
    self.session_locked = False


@internal # TODO :: probs not external
def _join_temple(temple_addr: address) -> bool:
    temple: Temple = Temple(temple_addr)
    assert(temple.join_temple_patrons()) # TODO :: is this how you do it ? or if statement
    self.temples.append(temple_addr)
    
    return True

@external # TODO :: probs not external
def join_temple(temple_addr: address) -> bool:
    return self._join_temple(temple_addr)


@external
def get_temples() -> DynArray[address, MAX_TEMPLES]:
    return self.temples


@external
def get_review_links_all() -> (
        DynArray[String[MAX_LINK_LEN], MAX_REVIEWS], 
        DynArray[String[MAX_LINK_LEN], MAX_REVIEWS],
        DynArray[h_session, MAX_REVIEWS]):
    return (
        self.session_reviews_by_self, 
        self.session_reviews_by_partners, 
        self.session_details)


@external
def get_review_links_by_partner() -> (DynArray[String[MAX_LINK_LEN], MAX_REVIEWS]):
    return self.session_reviews_by_partners

@external
def get_review_links_by_self() -> (DynArray[String[MAX_LINK_LEN], MAX_REVIEWS]):
    return self.session_reviews_by_self


@external
def add_review_by_self(
    rating: uint256, 
    link: String[MAX_LINK_LEN], 
    target_addr: address) -> bool:

    # TODO :: rm
    self.session_reviews_by_self.append(link)
    assert(GGHuman(target_addr).add_review_partner(rating, link) == True)

    # This is the author writing the review
    assert(msg.sender == owner_wallet_addr)

    # We have a pending review to do
    assert(self.session_locked == True) 

    # Check we are talking about the right person - ie latest review
    session: h_session = self.session_details[len(self.session_details) - 1]
    assert(session.partner == target_addr)

    # Add
    self.session_locked = False
    self.session_reviews_by_self.append(link)
    assert(GGHuman(target_addr).add_review_partner(rating, link) == True)
    return True


@external
def add_review_by_partner(_rating: uint256, link: String[MAX_LINK_LEN]) -> bool:
    """ Partner will call through a temple"""
    # TODO :: call from a temple contract
    # Find transaction

    self.session_reviews_by_partners.append(link)
    self.rating += _rating

    # Do we even need a review
    assert(len(self.session_details) != len(self.session_reviews_by_partners))

    # TODO:: reverese the list Look for last session with this partner
    for ii in range(MAX_REVIEWS):
        session: h_session = self.session_details[ii]

        if session.partner == msg.sender and self.session_reviews_by_partners[ii] == EMPTY_STR:
            self.session_reviews_by_partners[ii] = link
            self.rating += _rating
            return True

    return False
                    

@external
def add_session_info(_partner: address, _donation: uint256) -> bool:
    """ Temple will call to init a session"""
    session_temple: address = empty(address)

    # We are clear to have a session
    assert(self.session_locked == False)

    # This is one of our temples
    for ii in range(MAX_TEMPLES):
        if msg.sender == self.temples[ii]:
            session_temple = self.temples[ii]

    assert(session_temple != EMPTY_ADDR)

    # Init the session 
    session: h_session = h_session({
        partner: _partner,
        donation: _donation,
        temple: msg.sender,
        status: session_status.REQUESTED
    })

    self.session_details.append(session)

    # Get last session
    self.session_locked = True

    return True


@external
def update_profile_link(_profile_link: String[100]):
    # TODO :: Only TempleMaster can edit
    self.profile_link = _profile_link


@external
def update_division(_division: int128):
    assert (_division > 0)
    assert (_division <= 3)
    self.division = _division