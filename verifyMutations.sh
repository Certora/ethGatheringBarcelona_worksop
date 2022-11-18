SPECNAME="exampleSpec.spec"


certoraRun.py  EnglishAuction_ERC20.sol:EnglishAuction dependencies/DummyERC20A.sol dependencies/DummyERC721A.sol \
    --verify EnglishAuction:$SPECNAME \
    --link EnglishAuction:token=DummyERC20A \
    --link EnglishAuction:nft=DummyERC721A \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --send_only \
    --rule_sanity basic \
    --msg "$SPECNAME - EnglishAuction"


for FILE in Mutations/* 
do echo $FILE 
    certoraRun.py  $FILE:EnglishAuction dependencies/DummyERC20A.sol dependencies/DummyERC721A.sol \
        --verify EnglishAuction:$SPECNAME \
        --link EnglishAuction:token=DummyERC20A \
        --link EnglishAuction:nft=DummyERC721A \
        --solc solc8.13 \
        --staging \
        --optimistic_loop \
        --send_only \
        --rule_sanity basic \
        --msg "$SPECNAME - $FILE"
done