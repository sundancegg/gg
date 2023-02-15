# @version ^0.3.7

# enum wouldnt work in hashmap for some reason, maybe change these to bitwise flags
ERROR_SUCCESS: constant(uint8) = 1         # Can operate normally
ERROR_PENDING_REVIEW: constant(uint8) = 2  # Needs to finish a review
ERROR_BANNED: constant(uint8) = 3          # Not allowed to operate in temple
ERROR_PENDING_APROVAL: constant(uint8) = 4 # Waiting for approval from temple master

# Basic gg Session Status - 4 way transaction handshake
SESSION_SYN: constant(uint8) = 1            # Patron sends a request and donation
SESSION_ACK: constant(uint8) = 2            # Goddess Accepts
SESSION_DENY: constant(uint8) = 3           # Goddess takes a pass # TODO :: better name
SESSION_REVIEW: constant(uint8) = 4         # Both reviews have been submited
SESSION_FIN: constant(uint8) = 5            # All reviews have been submited, closed

# Basic record unit of the temple
struct t_session:
    goddess: address # TODO :: maybe have addr here
    patron: address
    donation: uint256
    session_id: uint256
    status: uint8
    # TODO :: maybe start / finish dates

# Goddess Guild addr
GoddessGuild: address

# Who has permission to be in this temple
# WalletAddress to status
TempleGoddessesM: HashMap[address, uint8]   # Goddesseses are members of one temple, 22 max team size #gridiron
TemplePatronsM: HashMap[address, uint8]     # Patrons are members of multiple temples
TempleGoddessesA: DynArray[address, 22]    # TODO:: O
TemplePatronsA: DynArray[address, 100]      # TODO:: How bad is 2x storage .....


# History of this temple - list of sessions
BookOfRecords: DynArray[t_session, 256] # TODO:: Obvs fix this

# Temple info
TempleName: public(String[100])
TempleDivision: public(uint256)
TempleMaster: public(address) # TODO :: cast to GoddessProfile addr
BaseRate: public(uint256)
TempleTreasury: uint256

# Payment structure - must equal 100
PercentToGoddess: constant(uint256) = 80
PercentToGG: constant(uint256) = 10
PercentToTempleMaster: constant(uint256) = 4
PercentToTemple: constant(uint256) = 3
PercentToVerifier: constant(uint256) = 3

# Division differential adjustment
# Patron pays to level up. Ie - D3 patron would need +1 for D2 and +2 for D1
# If patron is at the temple division or above, no adjustment is needed 
LevelUpOne: constant(uint256) = 10
LevelUpTwo: constant(uint256) = 20

# TODO:: probs should do this a cleaner way
DIV_PERCENT: constant(uint256) = 100

# Interfaces
# TODO :: import directly
interface GoddessProfile:
    def rating() -> int128: view

#contract PatronProfile:
#    def rating() -> int128: view
    

    # It is a good guideline to structure functions that interact
    # with other contracts (i.e. they call functions or send Ether)
    # into three phases:
    # 1. checking conditions
    # 2. performing actions (potentially changing conditions)
    # 3. interacting with other contracts
    # If these phases are mixed up, the other contract could call
    # back into the current contract and modify the state or cause
    # effects (Ether payout) to be performed multiple times.
    # If functions called internally include interaction with external
    # contracts, they also have to be considered interaction with
    # external contracts.


# Init all our basic values
@external
def __init__(_GoddessGuild: address, _TempleName: String[100], _TempleDivision: uint256, 
            _TempleMaster: address, _BaseRate: uint256):
    # TODO :: add aserts
    self.GoddessGuild = _GoddessGuild
    self.TempleName = _TempleName
    self.TempleDivision = _TempleDivision
    self.BaseRate = _BaseRate


# Patron calls to set up session... Maybe comes from gg account
@external
@payable
def patron_request_goddess(goddess_requested: address):
    assert(self.TemplePatronsM[msg.sender] == ERROR_SUCCESS)
    assert(self.TempleGoddessesM[goddess_requested] == ERROR_SUCCESS)
    
    # TODO :: ((self.BaseRate * divisionLevelAdjust) 
    # Check the divison of the patron/goddess for rate adjust
#GoddessProfile(self.TemplePatronsM[msg.sender]).rating()

    # Check if patron donation is high enough
    assert msg.value >= self.BaseRate
    
    # Hold money in escrow - Only payout once both reviews are in 
    ts: t_session = t_session({
        goddess: goddess_requested,
        patron: msg.sender,
        donation: msg.value,
        session_id: len(self.BookOfRecords), # TODO: this is probly not right
        status: SESSION_SYN})

    self.BookOfRecords.append(ts)


    # Check for submited rating / review

    # Update profiles

    # Release funds if ratints: t_session and reviews are over designated amt

    # Emite event if TM needs to investigate

    #

    # Check if bidding period has started.
    #assert block.timestamp >= self.auctionStart


# Goddess calls to onfirm a session
@external
def goddess_confirm_session(session_id: uint256) -> bool:
    session: t_session = self.BookOfRecords[session_id]
    assert(session.goddess == msg.sender)
    assert(self.TempleGoddessesM[msg.sender] == ERROR_SUCCESS)

    # TODO :: cant figure how to cast return struct from hashmap so this clunky way instead....
    session.status = SESSION_ACK
    self.BookOfRecords[session_id] = session

    return True


# Goddess calls to deny a session
@external
def goddess_deny_session(session_id: uint256) -> bool:
    session: t_session = self.BookOfRecords[session_id]
    assert(session.goddess == msg.sender)
    session.status = SESSION_ACK
    self.BookOfRecords[session_id] = session
    
    return True


# possibly some accting errors
@external
def session_payout(session_id: uint256):
    session: t_session = self.BookOfRecords[session_id]

    assert(session.status == SESSION_REVIEW)

    # assert reviews look good
    send(self.GoddessGuild, (PercentToGG * session.donation) / DIV_PERCENT)
    send(self.TempleMaster, (PercentToTempleMaster * session.donation) / DIV_PERCENT)
    send(session.goddess, (PercentToGoddess * session.donation) / DIV_PERCENT)
    # TODO get verifier:: send(session.verifier, (PercentToVerifier * session.donation) / DIV_PERCENT)
    self.TempleTreasury += (PercentToTemple * session.donation)  / DIV_PERCENT

    session.status = SESSION_FIN
    self.BookOfRecords[session_id] = session


# TODO :: needs permission of the temple master
# TODO :: fuix the fkn len access
@external
def join_temple_patrons() -> bool:
    # TODO :: need to fix attck of multiple submits
    self.TemplePatronsM[msg.sender] = ERROR_PENDING_APROVAL
    self.TemplePatronsA.append(msg.sender) # TODO : move this to after approval

    return True


# TODO :: needs permission of the temple master
@external
def join_temple_goddesses() -> bool:
    self.TempleGoddessesM[msg.sender] = ERROR_PENDING_APROVAL
    self.TempleGoddessesA.append(msg.sender) # TODO : move this to after approval

    return True


@external
def get_patrons() -> DynArray[address, 100]:
    return self.TemplePatronsA

@external
def get_goddesses() -> DynArray[address, 22]:
    return self.TempleGoddessesA