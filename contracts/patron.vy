# @version ^0.3.7

# Wallet owner
patron_wallet: immutable(address)

name: immutable(String[200])
rating: public(int128)
profile_link: public(String[100])
division: public(int128)
pending_review_lock: public(String[100]) # must write a review about last session before next
temples: public(DynArray[address, 50])

# TODO: This is obvs broken and bad design :(
review_links: public(DynArray[String[222], 128])

# TODO:
# temple_badges
# skill_badges

# Interfaces 
# TODO :: import directly
interface Temple:
    def join_temple_patrons() -> bool: payable # TODO :: marker


@external
def __init__(patron_wallet: address, name: String[200], 
        profile_link: String[100], division: uint256, temple: address):
    # TODO :: add aserts
    self.name = name
    self.profile_link = profile_link
    self.division = division
    self.patron_wallet = patron_wallet
    assert(join_temple(temple))


@external # TODO :: probs not external
def join_temple(temple_addr: address) -> bool:
    temple: Temple = Temple(temple_addr)
    assert(temple.join_temple_patrons()) # TODO :: is this how you do it ? or if statement
    self.temples.append(temple_addr)
    
    return True

@external
def get_temples() -> DynArray[address, 50]:
    return self.temples


@external
def get_review_links() -> DynArray[String[222], 128]:
    return self.review_links

   
@external
def update_name(_name: String[200]):
    self.name = _name


@external
def update_profile_link(_profile_link: String[100]):
    self.profile_link = _profile_link


@external
def add_review_link(_link: String[222]):
    assert (len(self.review_links) < 128) # TODO: fix this
    self.review_links.append(_link)


@external
def update_division(_division: int128):
    assert (_division > 0)
    assert (_division <= 3)
    self.division = _division