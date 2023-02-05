# Goddess Guild
GoddessGuild: address

# WalletAddress to ProfileContractAddress
ProfilesGoddesses: HashMap[address, address]
ProfilesPatrons: HashMap[address, address]

# Reciept to GoddessSession
Escrow: HashMap[uint256, GoddessSession]

# Temple info
TempleName: public(String)
TempleDivision: public(String)
TempleMaster: public(address)
BaseRate: public(uint256)
TempleWallet: public(uint256)

# Payment structure - must equal 1.00
PercentToGoddess: public(uint256) = .80
PercentToGG: public(uint256) = .10
PercentToTM: public(uint256) = .04
PercentToTemple: public(uint256) = .03
PercentToVerifier: public(uint256) = .03

# Division differential adjustment
# Patron pays to level up. Ie - D3 patron would need +1 for D2 and +2 for D1
# If patron is at the temple division or above, no adjustment is needed 
DivisionAdjustmentPlusOne: public(uint256) = .10
DivisionAdjustmentPlusTwo: public(uint256) = .20

# Defining a profile struct
struct GoddessSession:
    goddess: address
    patron: address
    donation: uint256
    session_id: uint256

# Init all our basic values
@external
def __init__(_GoddessGuild: address, _TempleName: String, _TempleDivision: uint256, 
            _TempleMaster: address, _BaseRate: uint256):
    # todo:: add aserts
    self.GoddessGuild = _GoddessGuild
    self.TempleName = _TempleName
    self.TempleDivision = _TempleDivision
    self.BaseRate = _BaseRate

# possibly some accting errors
def complet_session(session_reciept):
    # assert reviews look good
    session = Escrow[session_reciept]
    send(session.goddess, (PercentToTM * session.total_donation))
    send(GoddessGuild, (PercentToGG * session.total_donation))
    send(TempleMaster, (PercentToTM * session.total_donation))
    send(verifier, (PercentToVerifier * session.total_donation))
    TempleWallet += (PercentToTemple * session.total_donation)

    # delete the session?



# Patron calls to set up session... Maybe comes from gg account
@external
@payable
def request_goddess(goddess_requested: address, divisionLevelAdjust: uint256,):
    assert(ProfilesPatrons[msg.sender])
    assert(ProfilesGoddesses[goddess_requested])

    # Check if patron donation is high enough
    assert msg.value >= self.BaseRate + (self.BaseRate * divisionLevelAdjust)
    
    # Check the divison of the patron/goddess for rate adjust

    # Hold money in escrow 
    gs = GoddessSession({
        goddess: goddess_requested,
        patron: msg.sender,
        donation: msg.value})

    Escrow[msg.sender] = gs
    # Check for submited rating / review

    # Update profiles

    # Release funds if ratings and reviews are over designated amt

    # Emite event if TM needs to investigate

    #


    # Check if bidding period has started.
    assert block.timestamp >= self.auctionStart
    # Check if bidding period is over.
    assert block.timestamp < self.auctionEnd

    # Track the refund for the previous high bidder
    self.pendingReturns[self.highestBidder] += self.highestBid
    # Track new high bid
    self.highestBidder = msg.sender
    self.highestBid = msg.value
# Defining a profile struct
struct Profile:
    avg_rating: int128
    num_sessions: int128
    profile_link: String[128]

# Declaring a struct variable
exampleStruct: MyStruct = MyStruct({value1: 1, value2: 2.0})

# Accessing a value
exampleStruct.value1 = 1


# Set to true at the end, disallows any change
ended: public(bool)

# Keep track of refunded bids so we can follow the withdraw pattern
pendingReturns: public(HashMap[address, uint256])



# Bid on the auction with the value sent
# together with this transaction.
# The value will only be refunded if the
# auction is not won.
@external
@payable
def bid():
    # Check if bidding period has started.
    #assert block.timestamp >= self.auctionStart
    # Check if bidding period is over.
    #assert block.timestamp < self.auctionEnd
    # Check if bid is high enough
    assert msg.value > self.highestBid
    # Track the refund for the previous high bidder
    self.pendingReturns[self.highestBidder] += self.highestBid
    # Track new high bid
    self.highestBidder = msg.sender
    self.highestBid = msg.value

# Withdraw a previously refunded bid. The withdraw pattern is
# used here to avoid a security issue. If refunds were directly
# sent as part of bid(), a malicious bidding contract could block
# those refunds and thus block new higher bids from coming in.
@external
def withdraw():
    pending_amount: uint256 = self.pendingReturns[msg.sender]
    self.pendingReturns[msg.sender] = 0
    send(msg.sender, pending_amount)

# End the auction and send the highest bid
# to the beneficiary.
@external
def endAuction():
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

    # 1. Conditions
    # Check if auction endtime has been reached
    assert block.timestamp >= self.auctionEnd
    # Check if this function has already been called
    assert not self.ended

    # 2. Effects
    self.ended = True

    # 3. Interaction
    send(self.beneficiary, self.highestBid)
