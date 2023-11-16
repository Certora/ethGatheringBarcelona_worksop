SPECNAME="fullSpec.spec"


certoraRun  EnglishAuction.sol:EnglishAuction dependencies/DummyERC20A.sol dependencies/DummyERC721A.sol \
    --verify EnglishAuction:$SPECNAME \
    --link EnglishAuction:token=DummyERC20A \
    --link EnglishAuction:nft=DummyERC721A \
    --parametric_contracts EnglishAuction \
    --optimistic_loop \
    --rule_sanity basic \
    --msg "$SPECNAME - EnglishAuction with fullSpec"


for FILE in Mutations/* 
do echo $FILE 
    certoraRun  $FILE:EnglishAuction dependencies/DummyERC20A.sol dependencies/DummyERC721A.sol \
        --verify EnglishAuction:$SPECNAME \
        --link EnglishAuction:token=DummyERC20A \
        --link EnglishAuction:nft=DummyERC721A \
        --parametric_contracts EnglishAuction \
        --optimistic_loop \
        --rule_sanity basic \
        --msg "$SPECNAME - $FILE with fullSpec"
done