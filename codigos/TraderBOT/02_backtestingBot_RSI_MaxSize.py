import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import math
STOCK='AMZN'
cash=10000
year_list=[2016,2017,2018,2019]
renta_media_max=0
RSI_period_top=0
top_low=0
top_high=0
for RSI_period in range(9,26,1):
	for low_umbral in range(20,40,10):
		for high_umbral in range(60,80,10):
			renta_list=[]
			for year in year_list:
				class LongOnly(bt.Sizer):
					params = (('stake', 1),)
					def _getsizing(self, comminfo, cash, data, isbuy):
						if isbuy:
							divide = math.floor(cash/data.close[0])
							self.p.stake = divide
							return self.p.stake
						# Sell situation
						position = self.broker.getposition(data)
						if not position.size:
							return 0  # do not sell if nothing is open
						return self.p.stake

				class Strategy(bt.Strategy):
					def __init__(self):
						self.rsi = bt.indicators.RSI(period=RSI_period)
						self.dataclose = self.datas[0].close
						self.order = None

					def notify_order(self, order):
						if order.status in [order.Submitted, order.Accepted]:
						    # Buy/Sell order submitted/accepted to/by broker - Nothing to do
							return
						# Write down: no pending order
						self.order = None

					def next(self):
					#Si hay un orden en curso no hacer nada
						if self.order:
							return
						if not self.position:

							if self.rsi < low_umbral :
								self.buy()
						else:
							if self.rsi > high_umbral :
					  			self.sell()
					def stop(self):
						if self.position:
							self.sell()

				cerebro = bt.Cerebro()
				cerebro.addsizer(LongOnly)
				cerebro.addstrategy(Strategy)

				data = bt.feeds.YahooFinanceData(
				    dataname=STOCK,
				    fromdate=datetime.datetime(year, 1, 1),
				    todate=datetime.datetime(year, 12, 31),
				    reverse=False)

				cerebro.adddata(data)

				cerebro.broker.setcash(cash)

				cerebro.broker.setcommission(commission=0.001)

				cerebro.run()
				renta_list.append(((cerebro.broker.getvalue()-cash)/cash)*100)
				print('a fine {} tenemos:{}$'.format(year,cerebro.broker.getvalue()))
			renta_list=np.array(renta_list)
			renta_media=renta_list.mean()
			renta_std=renta_list.std()
			print('con periodo de RSI {} se obtiene una renta de: {}% con una desviation estandard de: {}%'.format(RSI_period,renta_media,renta_std))
			if renta_media > renta_media_max:
				renta_media_max=renta_media
				RSI_period_top=RSI_period
				top_low=low_umbral
				top_high=high_umbral
				top_cerebro=cerebro

print('El mejor periodo de RSI es {} dias con umbrales {}, {} y se obtiene una renta de: {}% con una desviation estandard de: {}%'.format(RSI_period_top,top_low,top_high,renta_media_max,renta_std))
top_cerebro.plot()[0][0]	

		
