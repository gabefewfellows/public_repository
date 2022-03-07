# Part 1: Import libraries
from terra_sdk.client.lcd import LCDClient
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.coins import Coins
from terra_sdk.core.fee import Fee
from terra_sdk.core.wasm import MsgExecuteContract
from terra_sdk.key.mnemonic import MnemonicKey

# Notes to Part 1:
# [1] Read more about the LCDClient class here: https://github.com/terra-money/terra.py/blob/e6528d268476841f0f4d77834116347bf7fb3de8/terra_sdk/client/lcd/lcdclient.py
# [2] Read more about the CreateTxOptions class here: https://github.com/terra-money/terra.py/blob/f25407271eb7d11f8d3a6fa197353c7142b84f20/terra_sdk/client/lcd/api/tx.py
# [3] Read more about the Coins class here: https://github.com/terra-money/terra.py/blob/a0c35bc7ee6cee700dc7e6a5ef861764769d7327/terra_sdk/core/coins.py
# [4] Read more about the Fee class here: https://github.com/terra-money/terra.py/blob/a0c35bc7ee6cee700dc7e6a5ef861764769d7327/terra_sdk/core/fee.py
# [5] Read more about the MsgExeucteContract class here: https://github.com/terra-money/terra.py/blob/f25407271eb7d11f8d3a6fa197353c7142b84f20/terra_sdk/client/lcd/api/tx.py
# [6] Read more about the MnemonicKey class here: https://github.com/terra-money/jigu/blob/98c580b3f72754bf7924488337305806ad14f08b/jigu/key/mnemonic.py

# Part 2: Set fixed global variables
TERRA_STD_MICRO_UNIT = 10**-6

MAP_TOKEN_PAIR_NAME_TO_ADDRESS = {
    "native_token_pairs": {
        "LUNA-UST": "terra1tndcaqxkpc5ce9qee5ggqf430mr2z3pefe5wj6"
    },
    "non-native_token_pairs": {}
}

# Part 3: Define utility functions
def get_coin_list(coins_like_string_object):
    return str(coins_like_string_object).split(",")


def get_coin_balance(coin_list):
    coin_balance = {}

    for coin in coin_list:
        coin_amount_string = ""
        coin_denom_string = ""

        for char in coin:
            if char.isnumeric():
                coin_amount_string += char
            else:
                coin_denom_string += char

        coin_balance[coin_denom_string] = round(int(coin_amount_string)*TERRA_STD_MICRO_UNIT, 6)

    return coin_balance


# Part 4: Define Terra blockchain interaction functions
def estimate_swap_result(token_pair_name):
    # TODO: Add doc string.
    
    token_pair_address = ""

    if MAP_TOKEN_PAIR_NAME_TO_ADDRESS["native_token_pairs"][token_pair_name]:
        token_pair_address = MAP_TOKEN_PAIR_NAME_TO_ADDRESS["native_token_pairs"][token_pair_name]
    else:
        token_pair_address = MAP_TOKEN_PAIR_NAME_TO_ADDRESS["non-native_token_pairs"][token_pair_name]


    estimated_swap_result = {}
    
    token_pair_lp = terra.wasm.contract_query(
        token_pair_address,
        {
            "pool":{}
        }
    )
    asset1_token_balance = float(token_pair_lp["assets"][0]["amount"])*TERRA_STD_MICRO_UNIT
    asset2_token_balance = float(token_pair_lp["assets"][1]["amount"])*TERRA_STD_MICRO_UNIT  
    
    estimated_price = asset1_token_balance/asset2_token_balance
    
    estimated_swap_result["estimated_price"] = estimated_price
    
    return estimated_swap_result


def do_swap(user_address, token_pair_name, token_offer_denom,
            token_offer_amount, swap_spread, gas_requested,
            tx_fee):
    # TODO: Add doc string.

    is_native_token = False
    token_pair_address = ""
    token_balance = ""

    swap_spread = str(swap_spread)
    swap_belief_price = str(estimate_swap_result(token_pair_name)["estimated_price"])
    swap_msg = ""
    swap_coins = None

    if MAP_TOKEN_PAIR_NAME_TO_ADDRESS["native_token_pairs"][token_pair_name]:
        is_native_token = True
        token_pair_address = MAP_TOKEN_PAIR_NAME_TO_ADDRESS["native_token_pairs"][token_pair_name]

        token_balance = get_coin_balance(
            get_coin_list(
                terra.bank.balance(trader_account_address)[0]
            )
        )
    else:
        token_pair_address = MAP_TOKEN_PAIR_NAME_TO_ADDRESS["non-native_token_pairs"][token_pair_name]

        token_balance = terra.wasm.contract_query(
            token_address,
            {
                "balance": {
                    "address": user_address
                }
            }
        )["balance"]

    buy_swap_msg = {
      "swap": {
        "max_spread": swap_spread,
        "offer_asset": {
          "info": {
            "native_token": {
              "denom": token_offer_denom
            }
          },
          "amount": token_offer_amount
        },
        "belief_price": swap_belief_price
      }
    }
    
    swap_msg = buy_swap_msg
    swap_coins = Coins.from_str(token_offer_amount + token_offer_denom)

    swap_tx = wallet.create_and_sign_tx(
        CreateTxOptions(
            msgs=[
                MsgExecuteContract(
                    sender=user_address,
                    contract=token_pair_address,
                    execute_msg=swap_msg,
                    coins=swap_coins
            )],
            fee=Fee(gas_limit=gas_requested, amount=tx_fee),
            memo=""
            
        )
    )

    completed_swap_tx = terra.tx.broadcast(swap_tx)

    return completed_swap_tx

# Part 5: Instantiate and set code run variables
# Part A: Instantiate the Terra LCD client and connect to the Terra blockchain
terra = LCDClient (chain_id="columbus-5", url="https://lcd.terra.dev")  # TODO #1

# Part B: Set the trader details
trader_account_address = "terra1stakewithatseltonstaketheseasvalidator"  # TODO #2
trader_mnemonic = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13 word14 word15 word16 word17 word18 word19 word20 word21 word22 word23 word24"  # TODO #3
mnemonicKey = MnemonicKey(mnemonic=trader_mnemonic)
wallet = terra.wallet(mnemonicKey)

# Part C: Set the swap details
token_pair_name = "LUNA-UST"  # TODO #4
token_pair_address = "terra1tndcaqxkpc5ce9qee5ggqf430mr2z3pefe5wj6"  # TODO #5
token_offer_denom = "uusd"  # TODO #6
token_offer_amount = str("1") + "000000"  # TODO #7

swap_spread = 0.01  # TODO #8
gas_wanted = 200374  # TODO #9
tx_fee = "100000" + "uusd"  # TODO #10

completed_swap_tx = do_swap(trader_account_address, token_pair_name,
                            token_offer_denom, token_offer_amount, swap_spread,
                            gas_wanted, tx_fee)

# End Notes:
# [1] As a reminder, this tutorial is for informational and educational purposes
# only. Nothing in this tutorial is advice - no financial, tax, legal or any
# other kind of advice. Do your own research and consult with professionals.
# [2] If you wish to write “stylistic” code, then consider adhering to a style
# guide. For reference, here is a publicly available Python style guide
# published by Google: https://google.github.io/styleguide/pyguide.html
# [3] If you read the Python style guide, then you are correct in seeing that
# this Python script provided does not currently follow the style guide
