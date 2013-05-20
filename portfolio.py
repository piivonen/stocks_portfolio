import sqlite3
import urllib.request
import helpers
from helpers import menu

DB = "portfolio.db"
conn = sqlite3.connect(DB)
cursor = conn.cursor()

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
        
def buy(user, ticker, share_num):
    sql = """select SharePrice from account where userid = ? and ticker = 'CASH'"""
    cursor.execute(sql, [(user)])
    cash_value = cursor.fetchall()
    cash_value = cash_value[0][0]
    market_price = price(ticker)
    #Make sure user user has enough cash
    purchase_cost = float(market_price) * float(share_num)
    if float(cash_value) >= purchase_cost:
        #If user already owns stock use update, if new stock then insert        
        sql = "SELECT shareprice, sharenum  FROM account where UserID =? and ticker = ?"
        cursor.execute(sql, [(user), (ticker)])
        hasTickerAlready = cursor.fetchall()
        if  hasTickerAlready:
            #update amount of shares and average share price
            prior_share_price = float(hasTickerAlready[0][0])
            prior_share_num = int(hasTickerAlready[0][1])
            new_share_num = int(prior_share_num) + int(share_num)
            new_share_price = ((prior_share_price*prior_share_num) + (market_price * share_num)) / (new_share_num) 
            updateValues = [new_share_price, new_share_num, user, ticker]
            sql = "UPDATE account SET shareprice = ?,  sharenum =?  WHERE userid = ? and ticker = ?"
            cursor.execute(sql, updateValues)
            conn.commit()
        else:
            #insert new ticker
            insertValues = [user, ticker, market_price, share_num]
            sql = "INSERT INTO account VALUES (?,?,?,?)"
            cursor.execute(sql, insertValues)
            conn.commit()
        #Deduct total share cost from cash value
            new_cash_value = cash_value - purchase_cost
            updateValues = [new_cash_value, user]
            sql = "UPDATE account SET shareprice = ? WHERE ticker = 'CASH' and userid = ?"
            cursor.execute(sql, updateValues)
            conn.commit()
        print("You successfully purchased "+str(share_num)+" share(s) of "+ticker+" @ $"+str(market_price)+" per share")
    else:
        print("You only have $", cash_value)


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


#UI
user = input("Enter a user name: ").lower()
sql = "SELECT UserID  FROM account where UserID =?"
cursor.execute(sql, [(user)])
usernameExists = cursor.fetchall()
if not usernameExists:
    item = [user, 'CASH',500000,1]
    cursor.execute('INSERT INTO account VALUES (?,?,?,?)', item)
    conn.commit()
    print("Welcome "+user+". $50,000 was deposited into your account")
else:
    print("Welcome back")

menu()
option = input("Your choice: ").strip(' ')

#VIEW

#BUY
if option == '2':
    stock_options = ['GOOG','AAPL','IBM','VTI','VNQ','TSLA']
    print("You can buy the following stocks: ",stock_options)
    while True:
        ticker = input("Enter ticker symbol: ").strip().upper()
        if ticker in stock_options:
            break 
    print("Current market value: "+ str(price(ticker)))
    cashDB = helpers.queryCash(user)
    while True:
        share_num = int(input("Enter number of shares to purchase: ").strip(' ')) 
        if cashDB < (share_num * market_price):
            print("Not enough cash. Buy less shares.")
        else:
            break
    buy(user, ticker, share_num)

#SELL
elif option =='3': 
    tickerDB = helpers.queryTickers(user);        
    while True:
        ticker = input("Enter ticker symbol: ").strip()
        if ticker in tickerDB:
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

