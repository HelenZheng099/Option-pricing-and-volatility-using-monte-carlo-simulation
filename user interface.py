import tkinter as tk
# from tkinter import messagebox
from tkinter import *
from tkinter.filedialog import *
from math import log, sqrt, pi, exp
from scipy.stats import norm
from datetime import datetime, date
import datetime as dt
import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import yfinance as yf
from pandas_datareader import data as pdr
import statistics
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def get_data(stock):
    # Retrieve stock data
    today = datetime.now() 
    one_year_ago = today.replace(year=today.year-1)
    yf.pdr_override()
    df = yf.download(stock, start=one_year_ago, end=today)
    df = df.sort_values(by="Date")
    df = df.dropna()
    df = df.assign(close_day_before=df.Close.shift(1))
    return df



def calculate_sigma(stock):
    df = get_data(stock)
    df['returns'] = np.log(df.Close) - np.log(df.close_day_before)
    sigma = df['returns'].std()
    return sigma


#calculate_sigma

def geometric_brownian(S0,sigma):
    # matrix store the results
    r=float(Entry6.get())
    T=int(Entry7.get())
    N=int(Entry8.get())
    i=int(Entry9.get())
    simulation_count=i

    S = np.zeros([T, simulation_count])
    print(S)
    S0_matrix = np.ones(simulation_count) * S0
    u = r / 252
    delta_t = 1 / N # each step takes 1/N day

    # run simulation N times a day for T days, totally N * T
    for y in range(N * T):
      S0_matrix *= np.exp((u - sigma**2 / 2) * delta_t + sigma * delta_t * np.random.normal(0, 1, size=[simulation_count]))
      if (y + 1) % N == 0: # end of day
        S[y // N, :] = S0_matrix
    print(S)
    return S

def get_stock_T(stock):
    r=float(Entry6.get())
    T=int(Entry7.get())
    N=int(Entry8.get())
    i=int(Entry9.get())

    df = get_data(stock)
    S0 = df.iloc[-1]['Close'] #initial stock price = current Close price 
    sigma = calculate_sigma(stock)
    S = np.zeros([T, i])
    S = geometric_brownian(S0, sigma)
    stock_0 = S0
    stock_T = np.array(S[-1, :], dtype=np.float16) # stock price at the end of day T
    return stock_T


def call(St):
    strike_price=float(Entry2.get())
    return np.maximum(St - strike_price, 0)

def calc_portfolio_value(stock_price, option_price, dim=2):
    stock_weight=float(Entry4.get())
    option_weight=float(Entry5.get())
    r=float(Entry6.get())
    T=int(Entry7.get())
    axis_val = 1 if dim == 2 else 0
    price_sum = stock_weight * stock_price + option_weight * option_price
    return price_sum / np.exp(r * T / 365)

def portfolio_value():
    strike_price=float(Entry2.get())
    stock_list=str(Entry1.get())
    stock_in_portfolio=str(Entry3.get())
    stock_weight=Entry4.get()
    option_weight=Entry5.get()
    r=float(Entry6.get())
    T=int(Entry7.get())
    N=int(Entry8.get())
    i=int(Entry9.get())
    #calculate call prices at T
    call_df = get_data(stock_list)
    print(call_df)
    call_S0 = call_df.iloc[-1]['Close'] #initial stock price = current Close price 
    stock_0 = call_S0
    stock_df= get_data(stock_in_portfolio)
    stock_S0 = stock_df.iloc[-1]['Close']

    stock_T = get_stock_T(stock_list)
    call_T = call(stock_T)
    #calculate stock price at T
    stock_price_T = get_stock_T(stock_in_portfolio)
    #calculate portfolio value at T
    portfolio_value_T = calc_portfolio_value(stock_price_T, call_T) 

    #calculate call prices at 0
    call_0 = call(stock_0)
    #calculate stock price at 0
    stock_price_0 = stock_S0 
    message1 =f"Call value at T = 0 is {call_0}"#改：分别对应不同股票
    # calculate portfolio value at 0
    portfolio_value_0 = calc_portfolio_value(stock_price_0, call_0, dim=1)
    message2 =f"The portfolio value at T = 0 is {portfolio_value_0}"
    # calculate portfolio return
    portfolio_return = portfolio_value_T / portfolio_value_0 - 1
    avg_portfolio_return = np.average(portfolio_return)
    message3 =f"The average portfolio return is {avg_portfolio_return}"
    # calculate VaR
    portfolio_return = np.sort(portfolio_return)
    value_at_risk = portfolio_return[int(0.05 * i)]       

    message4=f"VaR of the portfolio at {0.05 * 100}% confidence level: {value_at_risk}"
    message5=f"Amount required to cover minimum losses for one day is {str(portfolio_value_0* - np.percentile(portfolio_return,5))} "
    Text1.insert(tk.END, f"{message1}\n{message2}\n{message3}\n{message4}\n{message5}")


#Plot
def plot_stock_call(ax,canvas):
    stock_list=str(Entry1.get())
    r=float(Entry6.get())
    T=int(Entry7.get())
    df = get_data(stock_list)
    S0 = df.iloc[-1]['Close'] #initial stock price = current Close price 
    sigma = calculate_sigma(stock_list)
    S = geometric_brownian(S0, sigma)
    t = range(1, T+1, 1)
    ax.plot(t, S)
    ax.set_title('%s Days %d Sigma %.2f r %.2f S0 %.2f' % (stock_list, T, sigma, r, S0))
    ax.set_xlabel('Days')
    ax.set_ylabel('Stock Price')
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

def plot_stock_stock(ax,canvas):
    stock_in_portfolio=str(Entry3.get())
    r=float(Entry6.get())
    T=int(Entry7.get())
    df = get_data(stock_in_portfolio)
    S0 = df.iloc[-1]['Close'] #initial stock price = current Close price 
    sigma = calculate_sigma(stock_in_portfolio)
    S = geometric_brownian(S0, sigma)
    t = range(1, T+1, 1)

    ax.plot(t, S)
    ax.set_title('%s Days %d Sigma %.2f r %.2f S0 %.2f' % (stock_in_portfolio, T, sigma, r, S0))
    ax.set_xlabel('Days')
    ax.set_ylabel('Stock Price')
    ax.relim()
    ax.autoscale_view()
    canvas.draw()


root = Tk()
root.title('Monte Carlo Simulation')
root.geometry("800x1000") 

# stock = StringVar()
# strike_price= IntVar()
# stock_ticker=StringVar()
# Entry4.get()= DoubleVar(value=0.00)
# Entry5.get()= DoubleVar(value=0.00)
# r= DoubleVar(value=0.00)
# T= DoubleVar(value=0.00)
# N= IntVar()
# i= IntVar()



#Input Box
frame1=Frame(root)
frame1.grid(row=1, column=1, sticky="W")
frame1_option=Frame(frame1) #Error: cannot use geometry manager grid inside .!frame which already has slaves managed by pack
frame1_option.grid(row = 1, column=1, sticky="W")
frame1_others=Frame(frame1)
frame1_others.grid(row= 2, column=1, sticky="W")
# Output Box
frame2=Frame(root)
frame2.grid(row=2, column=1, sticky="W")
frame2_button=Frame(frame2)
frame2_box=Frame(frame2)
frame2_button.grid(row=1,column=1, sticky="W")
frame2_box.grid(row=2,column=1, sticky="W")
#Picture Box
frame3=Frame(root)
frame3.grid(row=3, column=1, sticky="W")
frame3_button=Frame(frame3)
frame3_box=Frame(frame3)
frame3_button.grid(row=1,column=1, sticky="W")
frame3_box.grid(row=2,column=1, sticky="W")

#frame1_option
L11=Label(frame1_option,text = "Stock Ticker (Call)")
L11.grid(row = 1, column = 1,padx=5.5,pady=5.5, sticky="W")
# L11=Label(frame1_option,text = "Stock Ticker List (Calls)")
Entry1= Entry(frame1_option)
Entry1.grid(row = 1, column = 3,padx=5.5,pady=5.5, sticky="W")
# Entry1= Entry(root,textvariable = strike_price())
L12=Label(frame1_option,text = "an uderlying stock of call, format: SPY ")
L12.grid(row = 1, column = 5,padx=5.5,pady=5.5, sticky="W")


L21=Label(frame1_option,text = "Strike Price")
Entry2= Entry(frame1_option)
L22=Label(frame1_option,text = "strike price, format: 370")

L31=Label(frame1_option,text = "Stock Ticker (Stock)")
Entry3= Entry(frame1_option)
L32=Label(frame1_option,text = "a stock included in the portfolio, format: GOOG")


L41=Label(frame1_option,text = "Stock Weight")
Entry4= Entry(frame1_option)
L42=Label(frame1_option,text = "select the weight of stock, format: 0.45")

L51=Label(frame1_option,text = "Call Weight")
Entry5=Entry(frame1_option)
L52=Label(frame1_option,text = "select the weight of calls, format: 0.55")

#frame1_others
L61=Label(frame1_others,text = "Risk Free Rate(r) ")
Entry6=Entry(frame1_others)

L71=Label(frame1_others,text = "Days before Expiration(T) ")
Entry7=Entry(frame1_others)

L81=Label(frame1_others,text = "Time Steps(N) ")
Entry8=Entry(frame1_others)

L91=Label(frame1_others,text = "Simulations(i) ")
Entry9=Entry(frame1_others)

#frame2_button
Button1=Button(frame2_button, text = "Option Value", command = portfolio_value)

#frame2_box
Text1 = Text(frame2_box, height=6, width=100)



#frame3_button
Button2=Button(frame3_button, text = "Simulation Graph(Option)", command = lambda: plot_stock_call(ax1,Canvas1))
Button3=Button(frame3_button, text = "Simulation Graph(Stock)", command = lambda: plot_stock_stock(ax2,Canvas2))

#frame3_box
fig1 = plt.Figure(figsize=(3.5, 3.5))
ax1 = fig1.add_subplot(111)
fig2 = plt.Figure(figsize=(3.5, 3.5))
ax2 = fig2.add_subplot(111)
Canvas1 = FigureCanvasTkAgg(fig1, master=frame3_box)
Canvas1_width = fig1.bbox.width + 5  # 可根据需要调整边距
Canvas1_height = fig1.bbox.height + 5  # 可根据需要调整边距
Canvas1.get_tk_widget().config(width=Canvas1_width, height=Canvas1_height)
Canvas2 = FigureCanvasTkAgg(fig2, master=frame3_box)
Canvas2_width = fig2.bbox.width + 5  # 可根据需要调整边距
Canvas2_height = fig2.bbox.height + 5 # 可根据需要调整边距
Canvas2.get_tk_widget().config(width=Canvas2_width, height=Canvas2_height)
# Canvas1.get_tk_widget().config(width=60, height=60)



# #frame1_option
# L11.grid(row = 1, column = 1,padx=5.5,pady=5.5)
# Entry1.grid(row = 1, column = 3,padx=5.5,pady=5.5)
# L12.grid(row = 1, column = 5,padx=5.5,pady=5.5)

L21.grid(row = 3, column = 1,padx=5.5,pady=5.5, sticky="W")
Entry2.grid(row = 3, column = 3,padx=5.5,pady=5.5, sticky="W") 
L22.grid(row = 3, column = 5,padx=5.5,pady=5.5, sticky="W")

L31.grid(row = 5, column = 1,padx=5.5,pady=5.5, sticky="W")
Entry3.grid(row = 5, column = 3,padx=5.5,pady=5.5, sticky="W") 
L32.grid(row = 5, column = 5,padx=5.5,pady=5.5, sticky="W")

L41.grid(row = 7, column = 1,padx=5.5,pady=5.5, sticky="W")
Entry4.grid(row = 7, column = 3,padx=5.5,pady=5.5, sticky="W") 
L42.grid(row = 7, column = 5,padx=5.5,pady=5.5, sticky="W")
L51.grid(row = 9, column = 1,padx=5.5,pady=5.5, sticky="W")
Entry5.grid(row = 9, column = 3,padx=5.5,pady=5.5, sticky="W") 
L52.grid(row = 9, column = 5,padx=5.5,pady=5.5, sticky="W")

# #frame1_others
L61.grid(row = 1, column = 1,padx=5.5,pady=5.5, sticky="W")
Entry6.grid(row = 1, column = 3,padx=5.5,pady=5.5, sticky="W")
L71.grid(row = 1, column = 5,padx=5.5,pady=5.5, sticky="W")
Entry7.grid(row = 1, column = 7,padx=5.5,pady=5.5, sticky="W")
L81.grid(row = 3, column = 1,padx=5.5,pady=5.5, sticky="W")
Entry8.grid(row = 3, column = 3,padx=5.5,pady=5.5, sticky="W") 
L91.grid(row = 3, column = 5,padx=5.5,pady=5.5, sticky="W")
Entry9.grid(row = 3, column = 7,padx=5.5,pady=5.5, sticky="W") 

# #frame2_button
Button1.grid(row = 1, column = 1,padx=5.5,pady=5.5, sticky="W") 
# #frame2_box
Text1.grid()

# #frame3_button
Button2.grid(row = 1, column = 1,padx=5.5,pady=5.5, sticky="W")
Button3.grid(row = 1, column = 3,padx=5.5,pady=5.5, sticky="W") 

# frame3_box
Canvas1.get_tk_widget().grid(row = 1, column = 1,sticky="W")
Canvas2.get_tk_widget().grid(row = 1, column = 2,sticky="W")

root.mainloop()


