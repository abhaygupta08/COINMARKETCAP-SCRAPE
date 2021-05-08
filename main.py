import requests
from bs4 import BeautifulSoup
import csv
import regex as re

##---------------------------------------------------------------------------------
#                       But Although site has a public API 
#	https://api.coinmarketcap.com/data-api/v3/map/all?listing_status=active,untracked
#-----------------------------------------------------------------------------------


def get_coins():
	## ----- 50x4 matrix for storing values
	store = [['' for j in range(4)] for i in range(50)]

	page = requests.get('https://coinmarketcap.com/coins/')
	
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find_all('table')[0]
	i = 1
	m = table.find_all('tr')
	
	## -- there is some differnce in 10-50
	for row in m[:11]:
		try:
			s = row.find_all('td')[2]
			data = s.find('a',class_='cmc-link')
			link = data['href']
			namSS = s.find_all('p')
			name,symbol = namSS[0].text,namSS[1].text
			# print(i,link,name,symbol,'\n')
			store[i-1] = [str(i),name,symbol,'coinmarketcap.com'+link]
			i+=1
		except:
			continue

	for row in m[11:51]:
		try:
			link = row.find('a',class_="cmc-link")['href']
			data = row.find_all('span')
			for d in data:
				if d.has_attr('class') and d['class'][0]=="crypto-symbol":
					symbol = d.text
					break
				elif not d.has_attr('class') and len(d.text)!=0:
					name = d.text
				
			# print(i,link,name,symbol,'\n')
			store[i-1] = [str(i),name,symbol,'coinmarketcap.com'+link]
			i+=1
		except:
			continue

	## ----- Stroring data to coins.csv
	with open('coins.csv', mode='w', newline='') as coins:
		s = csv.writer(coins, delimiter=',')
		s.writerow(['SNo.', 'Name', 'Symbol','URL'])
		s.writerow([''])
		for i in store:
			s.writerow(i)






def get_coin_data(symbol):
	try:
		with open('coins.csv') as f:
			reader = csv.reader(f)
			for row in reader:
				if len(row)==4 and row[2]==symbol:
					base = row
					break
	except:
		print("[-] ERROR  File Not Present")
	
	##### ----- base is row with encountered symbol
	try:
		rank = base[0]
		name = base[1]
		symbol = base[2]
		url = 'https://www.'+base[3]
	except UnboundLocalError:
		print('[-] ERROR  Symbol Not Found in CSV File')
		exit() #incase if not found


	## ----- requests get method
	a = requests.get(url)

	watchList = re.findall('namePill___3p_Ii">On ([^\s]*) watchlists',a.text)[0]
	# print(watchList)

	webSite = re.findall('buttonName___3G9lW">([^<]*)<',a.text)[0]
	# print(webSite)

	circulatingSupplyVAL = ''
	circulatingSupplyPERCENTAGE = ''
	try:
		circulatingSupplyVAL = re.findall('statsValue___2iaoZ">([^<]*)<',a.text)[4]
		circulatingSupplyPERCENTAGE = re.findall('supplyBlockPercentage___1g1SF">([^<]*)<',a.text)[0]
	except:
		pass
	# print(circulatingSupplyVAL,circulatingSupplyPERCENTAGE)

	price = re.findall('<\/strong><\/th><td>([^<]*)<',a.text)[0]
	# print(price)

	VolMarketCap = re.findall('Volume \/ Market Cap<\/th><td>([^<]*)<',a.text)[0]
	# print(VolMarketCap)

	marketDominance = re.findall('Market Dominance<\/th><td><span class="">([^<]*)<',a.text)[0] + ' %'
	# print(marketDominance)

	marketRank = re.findall('Market Rank<\/th><td>([^<]*)<',a.text)[0]
	# print(marketRank)

	temp = re.findall('Market Cap<\/th><td><span>([^<]*)<',a.text)
	marketCap = temp[0]
	fullyDilutedMarketCap = temp[1]
	# print(marketCap,fullyDilutedMarketCap)

	high = re.findall('All Time High<[^<]*<[^>]*>([^<]*)<[^<]*<[^<]*<[^<]*<[^<]*<[^<]*<[^<]*<span>([^<]*)<',a.text)
	allTimeHighDate = high[0][0]
	allTimeHighPrice = high[0][1]
	# print(allTimeHighDate,allTimeHighPrice)

	low = re.findall('All Time Low<[^<]*<[^>]*>([^<]*)<[^<]*<[^<]*<[^<]*<[^<]*<[^<]*<[^<]*<span>([^<]*)<',a.text)
	allTimeLowDate = low[0][0]
	allTimeLowPrice = low[0][1]
	# print(allTimeLowDate,allTimeLowPrice)



	des,founders,unique = '','',''
	soup = BeautifulSoup(a.text, 'html.parser')
	m = soup.find_all('h2')
	try:
		for i in m:
			if i.has_attr('id'):
				parent = i.findParent()
		j = 0
		temp = ''
		for i in list(parent.children):
			if j==3:
				break
			if i.name[0]=="h" and type(temp)==str:
				if len(temp)>0:
					if j==0:
						des = temp
					elif j==1:
						founders = temp
					elif j==2:
						unique = temp
					j+=1
				temp = ''
			elif i.name=="p":
				temp += i.text
	except:
		pass

	# print(des,'\n\n',founders,'\n\n',unique,'\n\n')

	#  -- SAVE TO CSV FILE
	with open('coins_data.csv', mode='w', newline='') as coins:
		s = csv.writer(coins, delimiter=',')
		
		s.writerow(['DATA OF COIN - '+symbol])
		s.writerow([''])  # newBlankLine
		
		s.writerow(['Symbol',symbol])
		s.writerow(['Name',name])
		s.writerow(['WatchList',watchList])
		s.writerow(['WebSite Url',webSite])
		s.writerow(['Circulating Supply %',circulatingSupplyVAL,circulatingSupplyPERCENTAGE])
		s.writerow(['Price',price])
		s.writerow(['Volume / Market Cap',VolMarketCap])
		s.writerow(['Market Dominance',marketDominance])
		s.writerow(['Rank',rank])
		s.writerow(['Market Cap',marketCap])
		s.writerow(['All Time High - DATE',allTimeHighDate])
		s.writerow(['All Time High - PRICE',allTimeHighPrice])
		s.writerow(['All Time Low  - DATE',allTimeLowDate])
		s.writerow(['All Time Low - PRICE',allTimeLowPrice])
		s.writerow(['What is '+symbol+' ?',des])
		s.writerow(['Who are the founders?',founders])
		s.writerow(['What makes it unique?',unique])
		






if __name__=="__main__":

	banner = '''SCRIPT DEVELOPED BY ABHAY GUPTA (abhay.19201@knit.ac.in) 
SCRAPE COINS DATA FOR TOP 50 BASED ON MARKETCAP

'''
	print(banner)
	print('Fetching List for Top 50 Coins...')
	
	get_coins()

	print('Fetch Done ! \n[+] File For List is Saved in coins.csv')


	symbol = input('Enter Symbol to Fetch Data: ').strip()
	get_coin_data(symbol)

	print('[+] File For DATA of ',symbol,'is Saved in coins_data.csv')