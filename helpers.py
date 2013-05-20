import sqlite3

DB = "portfolio.db"
conn = sqlite3.connect(DB)
cursor = conn.cursor()

#Query helpers    
def queryTickers(user):
    sql = """select Ticker from account where userid = ?"""
    cursor.execute(sql, [(user)])
    ticker = cursor.fetchall()
    return [r[0] for r in ticker]

def querySharenum(user,ticker):
    sql = """select ShareNum from account where userid = ? and Ticker = ?"""
    cursor.execute(sql, [(user),(ticker)])
    sharenum = cursor.fetchall()
    return sharenum[0][0]

def queryCash(user):
    sql = """select ShareNum from account where userid = ? and Ticker = 'CASH'"""
    cursor.execute(sql, [(user)])
    cash_value = cursor.fetchall()
    return cash_value[0][0]

#  print options
def menu():
    print("Welcome to your Python brokerage account")
    print("    1 - View balance")
    print("    2 - Buy stocks")
    print("    3 - Sell stocks")