from ib.opt import ibConnection, message
from ib.ext.Contract import Contract
from time import sleep
import lxml.etree





def fundamentalData_handler(msg):
	print(msg)
	#soup = lxml.etree.fromstring(msg)
	#for item in soup.xpath('//IssueID'):
	 #   print(item.attrib['Type'], ':', item.text)

def error_handler(msg):
    print(msg)

tws = ibConnection(port=7497, clientId=325)
tws.register(error_handler, message.Error)
tws.register(fundamentalData_handler, message.fundamentalData)
tws.connect()

c = Contract()
c.m_symbol = 'WPC'
c.m_secType = 'STK'
c.m_exchange = "SMART"
#c.m_primaryExch = "NYSE"
c.m_currency = "USD"

tws.reqFundamentalData(1,c,'ReportsFinSummary')
sleep(2)
