# This project is created to obtain data from exchange and do price forecast



import krakenex
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
import matplotlib.pyplot as plt
import math

# Package to play sound
import simpleaudio as sa

successWav = sa.WaveObject.from_wave_file('wav/success1.wav')
incorrectWav = sa.WaveObject.from_wave_file('wav/negative-beep.wav')
cashWav = sa.WaveObject.from_wave_file('wav/cash-register.wav')


# Variables Information
# Trading Variables
ArbSpread = 0.0055
TopupSpread = 0.00004
XRPLotSize = 1000
XRPFixVol = 120
VolumeThreshold = 200

# Initial Variables
ArbitrageOpp = 0
ArbitrageOppArray = []
Iterations = 0

GDticker = "eth-usd"


#Kraken Variables
#kraken.key is the file of API Key and Private Key
KrakenFile = open('krakenXRPAdd.txt', 'r')
KRippleAdd = KrakenFile.readline().splitlines()[0]
KWithdrawName = 'Arb'

#Kraken Authentication Info
k = krakenex.API()
k.load_key('kraken.key')
k.set_connection(krakenex.Connection())

ticker = "XXRPZUSD" #Kraken Ticker
KrakenURL = "Depth?pair=XXRPZUSD"
KOpenID = []


# Testing Area
# Connect to Krakenex API
k = krakenex.API()
k.load_key('kraken.key')

# Obtain OHLC on an interval of 1 minute
OHLC = k.query_public('OHLC', req = {'pair': 'XXRPZUSD',
                              'interval': 1})

OHLC = OHLC['result']
OHLC = OHLC['XXRPZUSD']

OHLC = pd.DataFrame.from_dict(OHLC, orient='columns')
OHLC.columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']

# OHLC['time'] = pd.to_datetime(OHLC['time'],  unit = 's')
# OHLC['close'] = OHLC['close'].astype(float)

# Missing data, how to interpolate?
# OHLC = OHLC.interpolate(method = 'linear')
plt.plot(OHLC['time'], OHLC['close'])
plt.show()