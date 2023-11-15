certoraRun  EnglishAuction.sol dependencies/DummyERC20A.sol dependencies/DummyERC721A.sol \
    --verify EnglishAuction:fullSpec.spec \
    --link EnglishAuction:token=DummyERC20A \
    --link EnglishAuction:nft=DummyERC721A \
    --parametric_contracts EnglishAuction \
    --optimistic_loop \
    --send_only \
    --rule_sanity basic \
    --msg "EnglishAuction"
