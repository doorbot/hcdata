import requests
import csv
from datetime import datetime,timedelta,date
from zipfile import ZipFile
from io import BytesIO

def mdrms(qtr):
	#retrieve zip file of MDRMs from BOG
	mdrm_url = 'https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip'
	bog_mdrm = requests.get(mdrm_url) 
	zf = ZipFile(BytesIO(bog_mdrm.content))
	mdrm = csv.reader(zf.open('MDRM_CSV.csv').read().decode('utf-8').split('\n'), delimiter=',')
	next(mdrm)
	mdrm_list = ['ID_RSSD','Institution Name','Report Date']
	mdrm_init = []
	for row in mdrm:
		if len(str(row).split(','))>1:
			#filter object for the current Y9 MDRMs
			if str(row).split(',')[7]==" 'FR Y-9C'" or str(row).split(',')[7]==" 'FR Y-9LP'" or str(row).split(',')[7]==" 'FR Y-9SP'":
				if datetime.strptime(str(row).split(',')[2].replace("'",'').strip(),'%m/%d/%Y %H:%M:%S %p').strftime('%Y%m%d') <= qtr.strftime('%Y%m%d') and datetime.strptime(str(row).split(',')[3].replace("'",'').strip(),'%m/%d/%Y %H:%M:%S %p').strftime('%Y%m%d') >= qtr.strftime('%Y%m%d'):
					mdrm_init += [str(row).split(',')[0].strip().replace('[','').replace("'",'')+str(row).split(',')[1].strip().replace('[','').replace("'",'')]
	mdrm_list.extend(set(mdrm_init))
	#adding back MDRMs that are ended prematurely or missing in the MDRM Data Dictionary
	missing_mdrms=['BHCKG334', 'BHCKG332', 'BHCKG335', 'BHCKG333', 'BHCKG299','BHCKHT69','BHCKJA21','BHCT2143','BHCKJA22','TEXTFT29','BHCPJJ33','BHCPHT70','BHCPHT69','TEXT5485','TEXT5486','TEXT5488','TEXT5487','TEXT5489']
	mdrm_list.extend(missing_mdrms)
	return mdrm_list

def reporters(qtr):
	#retrieve zip file of attributes latest from NPW
	attr_url = 'https://www.ffiec.gov/npw/FinancialReport/ReturnAttributesActiveZipFileCSV'
	npw_attr = requests.get(attr_url)
	zf = ZipFile(BytesIO(npw_attr.content))
	attr = csv.reader(zf.open('CSV_ATTRIBUTES_ACTIVE.CSV').read().decode('utf-8').split('\n'), delimiter=',')
	resp_list=[]
	for row in attr:
		if len(row)>1:
			#filer object for HC types--BHC, SLHC and IHC
			if row[3]=='1' or row[66]=='1' or row[-1]=='1':
				resp_list += [row[0]]
	return resp_list

def getData(rssd,form,qtr):
	dict={}
	#retrieve each as-of, ID_RSSD and report combination
	url = 'https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV?rpt='+str(form)+'&id='+str(rssd)+'&dt='+qtr.strftime('%Y%m%d')
	data = requests.get(url)
	if str(data.content)[0:10] == "b'ItemName":
		reader = csv.reader([l.decode('utf-8') for l in data.iter_lines()], delimiter=',')
	else:
		return dict
	for row in reader:
		if row != []:
			if row[0] not in ['Street Address', 'City', 'ItemName', 'State', 'Zip Code']:
				dict[row[0]]=row[-1]
	return dict

def main():
	#set as-of date to most recent as-of, a loop, function or declare for specific dates could be used instead
	if date.today().month%3==0:
		qtr = date(date.today().year,date.today().month-2,1) - timedelta(days=1)
	else:
		qtr = date(date.today().year,date.today().month - int(date.today().strftime('%m'))%3 + 1,1) - timedelta(days=1)
	
	mdrm_list=mdrms(qtr)
	rssd_list=reporters(qtr)

	#create pre-loop start time to display total program time when finished
	start_time = datetime.today()

	#output to local temp, could utilize qtr date into name
	with open('.//npw.csv','w',newline='') as f:
		fieldnames=mdrm_list
		#set columns up front to validate and order each report on write, also raise an error if any MDRMs exist in files that are not included in the MDRM zip file
		writer=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='raise')
		writer.writeheader()
		for id in rssd_list:
			#for debug and script progress monitoring
			print(id)
			dictData = {}
			#attempts to retrieve reports by ID_RSSD, skipping to the next if none are found, e.g. during non-semiannual as-of dates to bypass SP filers
			try:
				sp_data = getData(id,'FRY9SP',qtr)
				dictData.update(sp_data)
			except:
				continue
			try:
				c_data = getData(id,'FRY9C',qtr)
				dictData.update(c_data)
			except:
				continue
			try:
				lp_data = getData(id,'FRY9LP',qtr)
				dictData.update(lp_data)
			except:
				continue
			if len(dictData)>0:
				writer.writerow(dictData)
	#print start and end time
	print(start_time, datetime.today())

main()