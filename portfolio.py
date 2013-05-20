import sqlite3
import urllib.request
import helpers
from helpers import menu

DB = "portfolio.db"
conn = sqlite3.connect(DB)
cursor = conn.cursor()
fh = open('portfolio.log', 'a')

def price(ticker):
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s='+ticker+'&f=nsl1op&e=.csv'
    fh = urllib.request.urlopen(url)
    for line in fh:
        line = line.decode('utf-8')
        line = line.strip()
        if not line:
            continue
        else:
            market_price = line.split(',')
            return float(market_price[2])

def viewHolding(user):
    portfolio = helpers.queryHoldings
    for ticker in portfolio:
        print(portfolio[ticker])

def buy(user, ticker, sharenum):
    market_price = price(ticker)
    userStocks = helpers.queryTickers(user)   
    #update amount of shares and average share price
    if ticker in userStocks:
        values = helpers.queryPriorStock(user, ticker)        
        prior_shareprice = float(values[0])
        prior_sharenum = int(values[1])
        new_sharenum = prior_sharenum + share_num
        new_shareprice = ((prior_shareprice*prior_sharenum) + (market_price * sharenum)) / (new_sharenum) 
        updateValues = [new_shareprice, new_sharenum, user, ticker]
        sql = "UPDATE account SET shareprice = ?,  sharenum =?  WHERE userid = ? and ticker = ?"
        cursor.execute(sql, updateValues)
        conn.commit()
    else:
            #insert new ticker
        insertValues = [user, ticker, market_price, sharenum]
        sql = "INSERT INTO account VALUES (?,?,?,?)"
        cursor.execute(sql, insertValues)
        conn.commit()
    #Deduct total share cost from cash value
    cash = helpers.queryCash(user)
    cost = sharenum * market_price
    new_cash = cash - cost
    updateValues = [new_cash, user]
    sql = "UPDATE account SET shareprice = ? WHERE ticker = 'CASH' and userid = ?"
    cursor.execute(sql, updateValues)
    conn.commit()
        print("You successfully purchased "+str(share_num)+" share(s) of "+ticker+" @ $"+str(market_price)+" 
per share")
    fh.write(user+" bought "+str(share_num)+" share(s) of "+ticker+" @ $"+str(market_price))
    #logging.info('test')

def sell(user, ticker, share_num):
    sql = """select Ticker, SharePrice,ShareNum from account where userid = ? and ticker = ?"""
    cursor.execute(sql, [(user),(ticker)])
    row = cursor.fetchall()
    market_price = float(price(ticker))
    Ticker = row[0][0]
    SharePrice = row[0][1]
    ShareNum = row[0][2]
    share_num = int(share_num)
    # compute shares left after selling them
    shares_left = ShareNum - share_num
    SharePrice_new = share_num*market_price+SharePrice
    update = "update account set SharePrice = ? , ShareNum = ? where UserID = ? and Ticker=?"
    cursor.execute(update,[(SharePrice_new),(shares_left),(user),(ticker)])
    conn.commit()
    print("You have: ",str(helpers.querySharenum(user,ticker)) + " shares left.")
    fh.write(user+" sold "+str(share_num)+" share(s) of "+ticker+" @ $"+str(market_price))
#logging.('SOLD: %s share(s) of %s @ $%s', share_num, ticker, market_price)

#UI
user = input("Enter a user name: ").strip(' ').lower()
sql = "SELECT UserID  FROM account where UserID =?"
cursor.execute(sql, [(user)])
usernameExists = cursor.fetchall()
if not usernameExists:
    item = [user, 'CASH',500000,1]
    cursor.execute('INSERT INTO account VALUES (?,?,?,?)', item)
    conn.commit()
    print("Welcome "+user+". $50,000 was deposited into your account")

menu()
option = input("Your choice: ").strip(' ')

#VIEWS
if option == '1':
    viewHolding(user)

#option BUY
if option == '2':
    stock_options = ['GOOG','AAPL','IBM','VTI','VNQ','TSLA']
    cash = helpers.queryCash(user)
    print("You have $",cash," to spend")
    print("You can buy the following stocks: ",stock_options)
    while True:
        ticker = input("Enter ticker symbol: ").strip().upper()
        if ticker in stock_options:
            break
    market_price = price(ticker)
    print("Current market value: "+ str(market_price))
    #Make sure user has enough cash
    while True:
        share_num = int(input("Enter number of shares to purchase: ").strip(' ')) 
        if cash < (share_num * market_price):
            print("Not enough cash. Buy less shares.")
        else:
            break
    buy(user, ticker, share_num)

#option SELL
elif option =='3': 
    tickerDB = helpers.queryTickers(user);        
    print("You own shares of :", tickerDB)
    while True:
        ticker = input("Enter ticker symbol: ").strip()
        #probably should make sure user does not select cash
        if ticker in tickerDB and ticker:
            break;     
    sharenumDB = helpers.querySharenum(user,ticker)   
    while True:    
        share_num = input("Enter number of shares to sell: ").strip(' ') 
        #Make sure user has enough shares to sell 
        if int(share_num) <= sharenumDB:
            break;
    print("Current market value: " + str(price(ticker)))   
    sell(user,ticker,share_num)

conn.close()
