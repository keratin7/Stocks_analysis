import pandas as pd
import os
import time
from datetime import datetime

from time import mktime
import matplotlib.pyplot as plt

#from matplotlib import style
#style.use("dark background")

import re
import urllib


path = "/intraQuarter" 


def Key_Stats(gather="Total Debt/Equity (mrq)"):
    statspath = path+'/_KeyStats' #Adding the path
    stock_list = [x[0] for x in os.walk(statspath)] 
    df = pd.DataFrame(columns = ['Date',
                                 'Unix',
                                 'Ticker',
                                 'DE Ratio',
                                 'stock_p_change',
                                 'Price',
                                 'SP500',
                                 'sp500_p_change',
                                 'Difference',
                                 'Status'])

    sp500_df = pd.DataFrame.from_csv("YAHOO-INDEX_GSPC.csv")

    ticker_list = []

    for each_dir in stock_list[1:25]: #All apart from root dir
        each_file = os.listdir(each_dir)
        ticker = each_dir.split("/")[-1]    #The last part of the file path gives us the ticker(aapl)
        ticker_list.append(ticker)

        starting_stock_value = False
        starting_sp500_value = False


        if len(each_file)>0:    #Non-empty names
            for file in each_file:  

                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                #print(date_stamp, unix_time)
                full_file_path = each_dir+'/'+file  #Complete file path for all files
                #print(full_file_path)
                source = open(full_file_path,'r').read()    #source of html page
                #print(source)

                try:
                    try:
                        value = float(source.split(gather+':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0])
                    except Exception as e:
                        value = float(source.split(gather+':</td>\n<td class="yfnc_tabledata1">')[1].split('</td>')[0])
                        #print(str(e),ticker,file)
                        #time.sleep(15) 
                        #Split twice. Once before the value hence [1] Then after the value, hence [0]
                        print(ticker+':'+value)
                    try:
                        sp500_date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value = float(row["Adjusted Close"])
                    except:
                        sp500_date = datetime.fromtimestamp(unix_time-259200).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value = float(row["Adjusted Close"])

                    try:
                        stock_price = float(source.split('</small><big><b>')[1].split('</b></big>')[0])
                        #print "Stock price: ",stock_price," Ticker: ",ticker
                    except Exception as e:
                        try:
                            stock_price = float(source.split('</small><big><b>')[1].split('</b></big>')[0])
                            stock_price = re.search(r'(\d[1,8]\.\d[1,8])',stock_price)
                            stock_price = float(stock_price.group(1))

                            #print(stock_price)
                            #time.sleep(15)
                        except:
                            pass
                            #print('wtf stock price lol', ticker, file, value)
                            #time.sleep(5)

                    if not starting_stock_value:
                        starting_stock_value = stock_price

                    if not starting_sp500_value:
                        starting_sp500_value = sp500_value

                    stock_p_change = ((stock_price - starting_stock_value) / starting_stock_value) * 100
                    sp500_p_change = ((sp500_value - starting_sp500_value) / starting_sp500_value) * 100

                    difference = stock_p_change-sp500_p_change

                    if difference > 0:
                        status = "outperform"
                    else:
                        status = "underperform"

                    df = df.append({'Date':date_stamp,
                                    'Unix':unix_time,
                                    'Ticker':ticker,
                                    'DE Ratio':value,
                                    'Price':stock_price,
                                    'Stock_p_change':stock_p_change,
                                    'SP500':sp500_value,
                                    'sp500_p_change':sp500_p_change,
                                    'Difference':difference,
                                    'Status':status},ignore_index = True)
                    #All stock values of all companies are being appended to data frame df
                except Exception as e:
                    pass

    for each_ticker in ticker_list:
        try:
            plot_df = df[(df['Ticker']== each_ticker)]
            plot_df = plot_df.set_index(['Date'])

            if plot_df['Status'][-1] == "underperformed":
                color='r'
            else:
                color='g'

            plot_df['Difference'].plot(label=each_ticker, color= color)
            plt.legend()
        except:
            pass
    plt.show()
                
    save = gather.replace(' ','').replace(')','').replace('(','').replace('/','')+('.csv')
    print(save)
    df.to_csv(save)
                                                          
               
        

       
Key_Stats()
