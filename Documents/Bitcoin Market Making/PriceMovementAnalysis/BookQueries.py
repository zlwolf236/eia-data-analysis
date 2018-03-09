import krakenex

global KrakenBook

k = krakenex.API()
k.load_key('kraken.key')
k.set_connection(krakenex.Connection())
KrakenURL = "Depth?pair=XXRPZUSD"



def run_kraken_book():

    global KrakenBook

    try:
        KrakenBook = k.query_public(KrakenURL)
        print("Finish running Bookqueries")

    except Exception:
        k = krakenex.API()
        k.load_key('kraken.key')
        k.set_connection(krakenex.Connection())
        KrakenBook = k.query_public(KrakenURL)
        print("Finish running Bookqueries on Exception")

    return KrakenBook

count = 0

while count == 0:
    run_kraken_book()