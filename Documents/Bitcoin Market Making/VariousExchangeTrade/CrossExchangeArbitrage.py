# Most possible arbitrage opportunity is to make market at one of another
# And check the bid of the other exchange simultaneously, once matched, turn around and take the market at another exchange
# Why?
# Maker fee is 0.1% lesser than Taker fee, plus the spread is higher, thus margin is higher
#


# Problems to be solved
# 1) What if limit order is filled but market disappeared?
# 2) Kraken Exchange takes too long to take action

#USDT, Poloniex, Cryptrader



import krakenex
#import coinbase
import gdax #GDAX operates a continuous first-come, first-serve order book. Orders are executed in price-time priority
from bitstampy import api

#This is package to download live orderbook from BITSTAMP
#from pusher import Pusher

from coinbase.wallet.client import Client
#sudo pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.6.zip
from poloniex import Poloniex
#Use jason module to parse out a Python dictionary
#Use panda to convert dictionary into dataframe
import numpy as np
import pandas as pd
import datetime
import matplotlib as plt

# Package to play sound
import simpleaudio as sa

successWav = sa.WaveObject.from_wave_file('wav/success1.wav')
incorrectWav = sa.WaveObject.from_wave_file('wav/negative-beep.wav')
cashWav = sa.WaveObject.from_wave_file('wav/cash-register.wav')


# Variables Information
# Trading Variables
ArbSpread = 0.006
TopupSpread = 0.00007
XRPLotSize = 1000
XRPFixVol = 1500

# Initial Variables
ArbitrageOpp = 0
ArbitrageOppArray = []
Iterations = 0

GDticker = "eth-usd"


#Kraken Variables
#kraken.key is the file of API Key and Private Key
KrakenFile = open('krakenXRPAdd.txt', 'r')
KRippleAdd = KrakenFile.readline()

#Kraken Authentication Info
k = krakenex.API()
k.load_key('kraken.key')
k.set_connection(krakenex.Connection())

ticker = "XXRPZUSD" #Kraken Ticker
KrakenURL = "Depth?pair=XXRPZUSD"
KOpenID = []


# Bitstamp Variables
# Read Keys
BitFile = open('bitstampXRPkey.txt', 'r')
BSticker = "xrpusd" #Bitstamp Ticker
BitClientID = '421841'
BitAPIKey = BitFile.readline()      #Ripple yaoshi
BitAPISecret = BitFile.readline()   #Ripple mimi
BitRippleAdd = BitFile.readline()   #Ripple Qianbao
BitRippleDest = BitFile.readline()  #Ripple Destination tag

BitCluster = 'us2'
BitOpenID = []



#Source URL looks like this URL = "https://api.kraken.com/0/public/Trades?pair=XXBTZEUR&since=0"
#URL = "Ticker?pair=XXBTZUSD&since=0"


##############################################################################################
#################################### PROGRAM STARTS HERE #####################################
##############################################################################################

count = 0
while ArbitrageOpp < 6:

    ArbitrageOpp = 0

    #KRAKEN
    print("KRAKEN BOOK")
    #This query run on https://api.kraken.com/0/public/Ticker to generate data

    #Read dictionary
    try:
        result = k.query_public(KrakenURL)
        result = result["result"]
        result = result[ticker]

        KrakenTime = k.query_public('Time')
        KrakenTime = KrakenTime['result']
        KrakenTime = KrakenTime['unixtime']

    except Exception:
        try:
            k = krakenex.API()
            k.load_key('kraken.key')
            k.set_connection(krakenex.Connection())

        except Exception:
            pass


    #print("Kraken Data Time is", datetime.datetime.utcfromtimestamp(KrakenTime))


    # KAsks = result['asks']
    # KAsks = pd.DataFrame.from_dict(KAsks, orient='columns')
    # KAsks.columns = ['asks', 'volume', 'timestamp']
    # KAsks['timestamp'] = pd.to_datetime(KAsks['timestamp'], unit = 's')



    KBids = result['bids']
    KBids = pd.DataFrame.from_dict(KBids, orient='columns')
    KBids.columns = ['bids', 'volume', 'timestamp']
    KBids['timestamp'] = pd.to_datetime(KBids['timestamp'], unit = 's')


    # print(KAsks[:3])
    print(KBids[:3])


    #BITSTAMP
    print(" ")
    print("BITSTAMP BOOK")


    #Hardcoded api.order_book() implementation URL link, should be able to prompt user to choose which pair to implement
    BSbook = api.order_book()

    BSTime = BSbook['timestamp']
    print("Bitstamp time is", BSTime)

    # BSAsks = BSbook['asks']
    # BSAsks = pd.DataFrame.from_dict(BSAsks, orient='columns')
    # BSAsks.columns = ['volume', 'asks']
    # BSAsks['value_traded'] = BSAsks['volume'] * BSAsks['asks']
    #BSAsks['volume'] = round(BSAsks['volume'], 2)
    #BSAsks['value_traded'] = round(BSAsks['value_traded'], 2)


    BSBids = BSbook['bids']
    BSBids = pd.DataFrame.from_dict(BSBids, orient='columns')
    BSBids.columns = ['volume', 'bids']

    # print(BSAsks[:3])
    print(BSBids[:3])

    #Calculate Arbitrage Opportunity

    KBestBid = float(KBids['bids'][0])
    KBestBidVolume = float(KBids['volume'][0])

    BitBestBid = float(BSBids['bids'][0])
    BitBestBidVolume = float(BSBids['volume'][0])

    print("[", BitBestBidVolume, KBestBidVolume, "]")

    KBSpread = KBestBid - BitBestBid
    BKSpread = BitBestBid - KBestBid


    #If the Spread is more than 0.6%, assumed arbitrage opportunity exist
    #Next check if the spread is viable by checking the volume size, we will place the same size limit order on the other exchange
    # Procedure
    # 1) Place bid buy limit order at Bitstamp XRPUSD
    # 2) Once executed, transfer immediately to Bitstamp
    # 3) Once transferred to Kraken, sell at market at XRPUSD
    # 4) Wait for another opportunity
    if KBSpread > (ArbSpread*KBestBid):
        if KBestBidVolume > 1500:
            # Statistical Purposes
            ArbitrageOpp = 1

            # Play sound notify opportunity exist
            successWav.play()

            OrderLength = round(KBestBidVolume/XRPLotSize)
            BitLimitPrice = BitBestBid

            # Dont do for loop for now, let's just fix a volume of 1500
            # for i in range(1,OrderLength):
                # Place Bitstamp limit order, returned error if not enough fund available
                # Error can be shown by adding print(response) in calls.py
            BitOrder = api.buy_limit_order(client_id=BitClientID,
                                           api_key=BitAPIKey,
                                           api_secret=bytearray(BitAPISecret, 'utf-8'),
                                           amount=XRPFixVol,
                                           price=round(BitBestBid + TopupSpread, 5)
                                           )
            KBOpp = 1

            #Commented out for now, since insufficient fund
            #BitOrder = pd.DataFrame.from_dict(BitOrder, orient='columns')
            print(BitOrder)

            #Take down Order ID for Status purposes, commented out for now
            #BitOpenID.append(BitOrder['id'][0])


            while KBOpp == 1:
                print("Arbitrage exist, KrakenBid = ", KBestBid, " BitstampBid = ", BitBestBid)
                print("Gross Spread is ", (KBSpread / KBestBid * 100), "%")

                for i in range(0, len(BitOpenID)):

                    BitOrderStatus = api.order_status(client_id=BitClientID,
                                                      api_key=BitAPIKey,
                                                      api_secret=bytearray(BitAPISecret, 'utf-8'),
                                                      id = BitOpenID[i])

                    BitOrderStatus = pd.DataFrame.from_dict(BitOrderStatus, orient='columns')
                    print(BitOrderStatus['status'])

                    # Once Limit Order are filled, transfer to Kraken Exchange Immediately
                    if BitOrderStatus['status'][i] == "Finished":
                        AccountBalance = api.account_balance(client_id=BitClientID,
                                                             api_key=BitAPIKey,
                                                             api_secret=bytearray(BitAPISecret, 'utf-8'))

                        BitXRPBalance = float(AccountBalance['xrp_available'])

                        # Destination Tag is required for Kraken Deposit
                        BitTransfer = api.xrp_withdrawal(client_id=BitClientID,
                                                         api_key=BitAPIKey,
                                                         api_secret=bytearray(BitAPISecret, 'utf-8'),
                                                         amount=BitXRPBalance,
                                                         address=KRippleAdd,
                                                         destination_tag=BitRippleDest
                                                        )
                        print(BitTransfer)


                        # Check Kraken XRP Balance and Place Market Order
                        # Need fix balance retrieval method
                        KRippleBalance = k.query_private('Balance')
                        KRippleBalance = KRippleBalance['result']
                        print(KRippleBalance)


                        #Place Market Order at Kraken, Assumed Kraken already has some stock
                        KMktOrder = k.query_private("AddOrder", req={'pair': 'XXRPZUSD',
                                                                       'type': 'buy',
                                                                       'ordertype': 'market',
                                                                       'volume': float(KRippleBalance)})

                        print(KMktOrder)

                        # Trade successfully done sound
                        cashWav.play()

                        KBOpp = 0
                        # Transaction done


                # Monitor if Opportunity still exist
                try:
                    result = k.query_public(KrakenURL)
                    result = result["result"]
                    result = result[ticker]

                    KBids = result['bids']
                    KBids = pd.DataFrame.from_dict(KBids, orient='columns')
                    KBids.columns = ['bids', 'volume', 'timestamp']
                    KBids['timestamp'] = pd.to_datetime(KBids['timestamp'], unit='s')
                except Exception:
                    try:
                        k = krakenex.API()
                        k.load_key('kraken.key')
                        k.set_connection(krakenex.Connection())
                    except Exception:
                        pass

                BSbook = api.order_book()
                BSBids = BSbook['bids']
                BSBids = pd.DataFrame.from_dict(BSBids, orient='columns')
                BSBids.columns = ['volume', 'bids']

                KBestBid = float(KBids['bids'][0])
                BitBestBid = float(BSBids['bids'][0])

                KBSpread = KBestBid - BitBestBid
                BKSpread = BitBestBid - KBestBid


                # If opportunity still exist, but our placed order no longer the best execution price
                # Cancel old order and replace new order with higher bid

                if KBSpread > (ArbSpread*KBestBid) and BitBestBid > BitLimitPrice:
                    BitLimitPrice = BitBestBid  #Update new limit price

                    # Commented out for now, it was running well
                    # BitCancelStatus = api.cancel_order(client_id=BitClientID,
                    #                                    api_key=BitAPIKey,
                    #                                    api_secret=bytearray(BitAPISecret, 'utf-8')
                    #                                    )
                    # print("Order Cancel Status: ", BitCancelStatus)
                    BitOrder = api.buy_limit_order(client_id=BitClientID,
                                                   api_key=BitAPIKey,
                                                   api_secret=bytearray(BitAPISecret, 'utf-8'),
                                                   amount=XRPFixVol,
                                                   price=round(BitBestBid + TopupSpread, 5)
                                                   )
                    # Commented out for now, since insufficient fund
                    # BitOrder = pd.DataFrame.from_dict(BitOrder, orient='columns')
                    print(BitOrder)

                    BitOpenID = []

                    # Take down Order ID for Status purposes, commented out for now
                    # BitOpenID.append(BitOrder['id'][0])


                # Opportunity disappeared
                # Cancel Order, Cancel OrderID book
                # End loop

                if KBSpread < (ArbSpread*KBestBid):


                    #Commented out for now, it is running well
                    # BitCancelStatus = api.cancel_order(client_id=BitClientID,
                    #                                    api_key=BitAPIKey,
                    #                                    api_secret=bytearray(BitAPISecret, 'utf-8')
                    #                                    )
                    # print("Order Cancel Status: ", BitCancelStatus)
                    BitOpenID = [] #No more Open Order
                    KBOpp = 0

                    #Play sound when opportunity disappeared
                    incorrectWav.play()

        else:
            print("Not enough volume to trade")




    #If BitBestBid is higher than KBestBid for more than 0.6%, assumed arbitrage opportunity exist
    # Procedure
    # 1) Place bid buy limit order at Kraken XRPUSD
    # 2) Once executed, transfer immediately to Bitstamp
    # 3) Once transferred to Bitstamp, sell at market at XRPUSD
    # 4) Wait for another opportunity
    if BKSpread > (ArbSpread*BitBestBid):
        if BitBestBidVolume > 1500:
            # Statistical purposes
            ArbitrageOpp = 1

            # Playsound notify opportunity exist
            successWav.play()

            # Update New Kraken LimitPrice
            KLimitPrice = KBestBid

            try:
                KLimitOrder = k.query_private("AddOrder", req={'pair': 'XXRPZUSD',
                                                            'type': 'buy',
                                                            'ordertype': 'limit',
                                                            'price': round(KLimitPrice + TopupSpread, 5),
                                                            'volume': XRPFixVol})

            except Exception:
                OrderPass = 0
                while OrderPass == 0:
                    count = 1
                    print("Reordering attempt: ", count)
                    count = count + 1
                    try:
                        k = krakenex.API()
                        k.load_key('kraken.key')
                        KLimitOrder = k.query_private("AddOrder", req={'pair': 'XXRPZUSD',
                                                                    'type': 'buy',
                                                                    'ordertype': 'limit',
                                                                    'price': round(KLimitPrice + TopupSpread, 5),
                                                                    'volume': XRPFixVol})
                        OrderPass = 1
                    except Exception:
                        pass


            BKOpp = 1

            # Tested part, "Insufficient fund", commented out for now
            # KLimitOrder = KLimitOrder['result']
            # KLimitOrder = KLimitOrder['txid']
            # KLimitOrder = pd.DataFrame.from_dict(KLimitOrder, orient='columns')
            print(KLimitOrder)

            #Take down Order ID for Status purposes
            # KOpenID.append(KLimitOrder['id'][0])


            while BKOpp == 1:
                print("Arbitrage exist, KrakenBid = ", KBestBid, " BitstampBid = ", BitBestBid)
                print("Gross Spread is ", (BKSpread / BitBestBid * 100), "%")

                for i in range(0, len(KOpenID)):
                    KOrderStatus = k.query_private("QueryOrders", req={'pair': str(KOpenID[i])})
                    KOrderStatus = KOrderStatus['result']
                    KOrderStatus = pd.DataFrame.from_dict(KOrderStatus, orient='columns')

                    # If Kraken Bid order is filled, place market sell at Bitstamp
                    if KOrderStatus['status'][i] == 'closed':
                        KWithdraw = k.query_private("Withdraw", req={'asset': 'XXRP',
                                                                       'key': BitRippleAdd,
                                                                       'amount': 1000})

                        BitMktOrder = api.buy_limit_order(client_id=BitClientID,
                                                         api_key=BitAPIKey,
                                                         api_secret=bytearray(BitAPISecret, 'utf-8'),
                                                         amount=XRPFixVol)
                        print(BitMktOrder)

                        # Trade successfully done sound
                        cashWav.play()
                        BKOpp = 0

                # Monitor if Opportunity still exist
                try:
                    result = k.query_public(KrakenURL)
                    result = result["result"]
                    result = result[ticker]
                except Exception:
                    try:
                        k = krakenex.API()
                        k.load_key('kraken.key')
                        k.set_connection(krakenex.Connection())
                    except Exception:
                        pass

                KBids = result['bids']
                KBids = pd.DataFrame.from_dict(KBids, orient='columns')
                KBids.columns = ['bids', 'volume', 'timestamp']
                KBids['timestamp'] = pd.to_datetime(KBids['timestamp'], unit='s')

                BSbook = api.order_book()
                BSBids = BSbook['bids']
                BSBids = pd.DataFrame.from_dict(BSBids, orient='columns')
                BSBids.columns = ['volume', 'bids']

                KBestBid = float(KBids['bids'][0])
                BitBestBid = float(BSBids['bids'][0])

                KBSpread = KBestBid - BitBestBid
                BKSpread = BitBestBid - KBestBid


                # If opportunity still exist, but our placed order no longer the best execution price
                # Cancel old order and replace new order with higher bid

                if BKSpread > (ArbSpread*BitBestBid) and KBestBid > KLimitPrice:
                    # Update new Kraken Limit Price
                    KLimitPrice = KBestBid

                    # Cancel Old Orders
                    try:
                        KCancelOrder = k.query_private("CancelOrder", req={'txid': KOpenID})

                    except Exception:

                        CancelPass = 0
                        while CancelPass == 0:
                            count = count + 1
                            print("Recancelling attempt: ", count)
                            try:

                                k = krakenex.API()
                                k.load_key('kraken.key')
                                KCancelOrder = k.query_private("CancelOrder", req={'txid': KOpenID})

                                #Delete Cancelled order id
                                KOpenID = []

                                CancelPass = 1

                            except Exception:
                                pass


                    print("Order Cancel Status: ", KCancelOrder)


                    # Place new order with higher bid
                    try:
                        KLimitOrder = k.query_private("AddOrder", req={'pair': 'XXRPZUSD',
                                                                       'type': 'buy',
                                                                       'ordertype': 'limit',
                                                                       'price': round(KLimitPrice + TopupSpread, 5),
                                                                       'volume': XRPFixVol})

                    except Exception:
                        OrderPass = 0
                        count = 1
                        while OrderPass == 0:

                            print("Reordering attempt: ", count)
                            count = count + 1
                            try:
                                k = krakenex.API()
                                k.load_key('kraken.key')
                                KLimitOrder = k.query_private("AddOrder", req={'pair': 'XXRPZUSD',
                                                                               'type': 'buy',
                                                                               'ordertype': 'limit',
                                                                               'price': round(KLimitPrice + TopupSpread, 5),
                                                                               'volume': XRPFixVol})
                                OrderPass = 1
                            except Exception:
                                pass


                    # Delete old order ID and record new one
                    KOpenID = []

                    # Tested part, "Insufficient fund", commented out for now
                    # KLimitOrder = KLimitOrder['result']
                    # KLimitOrder = KLimitOrder['txid']
                    # KLimitOrder = pd.DataFrame.from_dict(KLimitOrder, orient='columns')
                    print(KLimitOrder)

                    # Take down Order ID for Status purposes
                    # KOpenID.append(KLimitOrder['id'][0])


                # If Opportunity disappeared, cancel all orders
                if BKSpread < (ArbSpread * BitBestBid):
                    try:
                        KCancelOrder = k.query_private("CancelOrder", req={'txid': KOpenID})

                    except Exception:
                        CancelPass = 0
                        while CancelPass == 0:
                            count = count + 1
                            print("Recancelling attempt: ", count)
                            try:

                                k = krakenex.API()
                                k.load_key('kraken.key')
                                KCancelOrder = k.query_private("CancelOrder", req={'txid': KOpenID})

                                CancelPass = 1

                            except Exception:
                                pass




                    print("Order Cancel Status: ", KCancelOrder)
                    KOpenID = []  # No more Open Order
                    BKOpp = 0

                    # Play sound when opportunity disappeared
                    incorrectWav.play()

        else:
            print("Not enough volume to trade")


    ArbitrageOppArray.append(ArbitrageOpp)
    Iterations = Iterations + 1

    # print(PKSpread, KPSpread, PBSpread, BPSpread, KBSpread, BKSpread)
    print("KB current spread is : ", KBSpread/KBestBid*100, "%")
    print("BK current spread is : ", BKSpread/BitBestBid*100, "%")
    print("Arbitrage Opportunity = ", ArbitrageOpp)
    print("System has ran : ", Iterations, " times")
    print("***************************************************************************************************************")


    #Testing Area


    # #COINBASE
    # print("This part is CoinBase Code")


    # #Coinbase Asks
    # CBAsks = CBClient.get_buy_price(currency_pair = 'XRP-USD')
    # CBBids = CBClient.get_sell_price(currency_pair = 'XRP-USD')
    #
    # print(CBAsks)
    # print(CBBids)
    #
    #
    #
    # #GDAX (Formerly Coinbase)
    # print("This part is GDAX Code")
    # public_client = gdax.PublicClient()
    #
    # print(public_client.get_product_ticker(product_id=GDticker))
    # print(public_client.get_products())



    #BITFINEX



print("The spread are:")
print(SpreadSize)
print("***************************************************************************************************************")
