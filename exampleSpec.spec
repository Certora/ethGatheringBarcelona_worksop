/*
   This is a specification file for EnglishAuction's formal verification
   using the Certora prover.
 */


 import "erc20.spec";

// Reference from the spec to additional contracts used in the verification.
using DummyERC721A as NFT;
using DummyERC20A as Token;


/*
    Declaration of methods that are used in the rules. envfree indicate that
    the method is not dependent on the environment (msg.value, msg.sender, etc.).
    Methods that are not declared here are assumed to be dependent on env.
*/


methods {
    // auction getters
    function seller()                    external returns (address) envfree;
    function nftId()                     external returns (uint) envfree;
    function nft()                       external returns(address) envfree;
    function endAt()                     external returns (uint256) envfree;
    function started()                   external returns (bool) envfree;
    function ended()                     external returns (bool) envfree;
    function highestBidder()             external returns (address) envfree;
    function highestBid()                external returns (uint256) envfree;
    function bids(address)               external returns (uint256) envfree;
    function operators(address, address) external returns (bool) envfree;


    // erc721
    function _.safeTransferFrom(address, address, uint256) external => DISPATCHER(true);
    function NFT.balanceOf(address) external returns (uint256) envfree;
    function NFT.ownerOf(uint256) external returns (address) envfree;
    /* NONDET implies that the function is treated as a non state changing;
       function that returns arbitrary value */
    function _.onERC721Received( address,address,uint256,bytes) external => NONDET;

    //erc20
    function Token.balanceOf(address) external returns (uint256) envfree;
}


/*-----------------------------------------------
|                  Properties                   |
-----------------------------------------------*/


/******************************
*           Unit Test         *
******************************/


/* Property: Integrity of end() time

   Description: Impossible to end earlier (version 1 - end() could be successfully executed only if assert is true)

   This is an example of a simple unit test: for all states, for all block.timestamp
   if end() succeeded then block.timestamp must be at least endAt()
   Note that as default only non reverting paths are reasoned

*/
rule integrityOfEndTime(env e) {
    end(e);

    assert e.block.timestamp >= endAt(), "ended before endAt";
}


/* Property: Integrity of end() time

   Description: Impossible to end earlier (version 2 - end() should revert under required condition)

   Same property as above but implemented with taking into account reverting path and reasoning about the case of lastReverted

*/
// Impossible to end earlier (
rule impossibleToEndEarlier(env e, method f) {
    require e.block.timestamp < endAt();

    end@withrevert(e);

    assert lastReverted, "ended before endAt";
}



/******************************
*       Variable Transition   *
******************************/

/*
   Property: Monotonicity of highest bid
   Description: highestBid can't decrease (if we consider only bid functions, can use >)

   Implemented as a parametric rule, a rule that is verified on all external\public functions of the contract
*/
rule monotonicityOfHighestBid(method f) {
    uint before = highestBid();

    env e;
    calldataarg args;
    f(e, args);

    assert highestBid() >= before;
}


/******************************
*       State Transition      *
******************************/


/* Property: Once ended Always ended

   Description: If the auction is at ended state it stays ended after every possible transaction

   Implemented with an implication which can be written as:

   if (before) {
      assert (ended());
   }
   else
      assert (True);  <---- always hold

*/
rule onceEndedAlwaysEnded(method f) {
    env e;
    calldataarg args;

    bool before = ended();
    f(e, args);
    assert before => ended();
}



/******************************
*        Valid State          *
******************************/

/* Property: Others bids are less than the highestBid

   Implemented as an invariant - an expression that must hold on all states.

   NOTE: This is failing, let's understand why and fix the rule

*/
invariant integrityOfHighestBidStep(address other)
     other != highestBidder()  => bids(other) < highestBid();



/******************************
*       High Level            *
******************************/



/******************************
*       Risk Assessment       *
******************************/

/* Property: changeToNFTOwner

   Description: NFT Owner does not change except on end() and start()

   Here there is a call to the NFT contract. Also note the use of f.selector to reference a specific function

   This property can be strengthened
*/
rule changeToNFTOwner(env e, method f) {
    address nftOwnerBefore = NFT.ownerOf(nftId()); /* reference to another contract */

    address operator; address bidder;

    callFunctionHelper(e, f, operator, bidder);    /* use of a CVL function just for fun */

    address nftOwnerAfter = NFT.ownerOf(nftId());

    assert nftOwnerAfter != nftOwnerBefore  => ( f.selector == sig:end().selector || f.selector == sig:start().selector );
}





/*-----------------------------------------------
|              Ghosts and hooks                 |
-----------------------------------------------*/

/* This ghost is like an additional variable that tracks changes to the bids mapping */
/* mathint are the whole range of integer values (unlimited) */
ghost mathint sumBids {
    init_state axiom sumBids == 0 ;
}

/* whenever bids[user] is updated to newValue where previously it held oldValue
   update sumBind */
hook Sstore bids[KEY address user] uint256 newValue (uint256 oldValue) STORAGE {
    sumBids = sumBids + newValue - oldValue;
}

// simple rule that uses the ghost and filters

rule justUseGhost(method f) {
    mathint before = sumBids;
    env e;
    calldataarg args;
    f(e,args);
    assert sumBids != before => true;
}

/*-----------------------------------------------
|           Helper Functions                    |
-----------------------------------------------*/

/* These helper functions are example and can help in reasoning about the different cases */

function callBidFunction(method f, env e, uint amount, address bidder) returns bool {
    if (f.selector == sig:bid(uint).selector ) {
        bid@withrevert(e, amount);
        return !lastReverted;
    }
    else {
        bidFor@withrevert(e, bidder, amount);
        return !lastReverted;
    }
}


function callFunctionHelper(env e, method f, address operator, address bidder) {
    uint256 amount;
    require e.msg.sender == operator;
    if (f.selector == sig:withdrawAmount(address, uint).selector) {
        withdrawAmount(e, bidder, amount);
    } else if  (f.selector == sig:withdrawFor(address, uint).selector ){
        withdrawFor(e, bidder, amount);
    }
    else if (f.selector == sig:bidFor(address, uint).selector) {
        bidFor(e, bidder, amount);
    }
    else if (f.selector == sig:end().selector) {
        end(e);
    }
    else {
        calldataarg args;
        f(e, args);
    }
}
