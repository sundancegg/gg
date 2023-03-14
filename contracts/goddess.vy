# @version ^0.3.7


# Wallet owner
owner_wallet_addr: immutable(address)

name: immutable(String[200])
rating: public(int128)
profile_link: public(String[100])
#division: public(int128)
pending_review_lock: int128 # must write a review about last session before next
temples: public(DynArray[address, 50])

# TODO: This is obvs broken and bad design :(
review_links: public(DynArray[String[222], 128])

# TODO:
# temple_badges
# skill_badges

# Interfaces 
# TODO :: import directly
interface Temple:
    def join_temple_goddesses() -> bool: payable # TODO :: marker


@external
def __init__(_owner_wallet_addr: address, _name: String[200], 
        profile_link: String[100], temple: address):
    # TODO :: add aserts
    owner_wallet_addr = _owner_wallet_addr
    name = _name
    self.profile_link = profile_link
    assert(self._join_temple(temple))


@internal # TODO :: probs not external
def _join_temple(temple_addr: address) -> bool:
    temple: Temple = Temple(temple_addr)
    assert(temple.join_temple_goddesses()) # TODO :: is this how you do it ? or if statement
    self.temples.append(temple_addr)
    
    return True

@external # TODO :: probs not external
def join_temple(temple_addr: address) -> bool:
    return self._join_temple(temple_addr)


@external
def get_temples() -> DynArray[address, 50]:
    return self.temples


@external
def get_review_links() -> DynArray[String[222], 128]:
    return self.review_links


@external
def update_profile_link(_profile_link: String[100]):
    self.profile_link = _profile_link


@external
def add_review_link(_link: String[222]):
    assert (len(self.review_links) < 128) # TODO: fix this
    self.review_links.append(_link)
