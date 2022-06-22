import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import math

STOCK='AMZN'
cash=10000
year_list=[2016,2017,2018,2019]
renta_media_max=0
SMA_period_min_top=0
SMA_period_max_top=0
for SMA_period_min in range(16,20,2):
	for SMA_period_max in range(36,54,2):
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
					self.dataclose = self.datas[0].close
					self.smaR = bt.indicators.SimpleMovingAverage(period=SMA_period_min)
					self.smaL = bt.indicators.SimpleMovingAverage(period=SMA_period_max)
					#self.sma4 = bt.indicators.SimpleMovingAverage(period=4)
					self.buysig = bt.ind.CrossOver(self.smaR, self.smaL)
					self.sellsig = bt.ind.CrossOver(self.smaR, self.dataclose)
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
						if self.buysig>0:
							self.buy()
					else:

						if self.sellsig>0:
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
		print('con media movil rapida {} y media movil lenta {} se obtiene una renta de: {}% con una desviation estandard de: {}%'.format(SMA_period_min,SMA_period_max,renta_media,renta_std))
		if renta_media>renta_media_max:
			renta_media_max=renta_media
			SMA_period_min_top=SMA_period_min
			SMA_period_max_top=SMA_period_max
			top_cerebro=cerebro

print('La mejor combinacion es media rapida {} dias y media lenta {} dias, se obtiene una renta de: {}% con una desviation estandard de: {}%'.format(SMA_period_min_top,SMA_period_max_top,renta_media_max,renta_std))	
top_cerebro.plot()[0][0]



		
