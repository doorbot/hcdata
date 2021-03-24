import requests
import csv
import sys
from datetime import datetime,timedelta,date
from zipfile import ZipFile
from io import BytesIO

qtr = date(date.today().year,date.today().month - int(date.today().strftime('%m'))%3 + 1,1) - timedelta(days=1)

def mdrms():
	mdrm_url = 'https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip'
	bog_mdrm = requests.get(mdrm_url)
	zf = ZipFile(BytesIO(bog_mdrm.content))
	mdrm = csv.reader(zf.open('MDRM_CSV.csv').read().decode('utf-8').split('\n'), delimiter=',')
	next(mdrm)
	mdrm_list = ['ID_RSSD','Institution Name','Report Date']
	for row in mdrm:
		if len(str(row).split(','))>1:
			if str(row).split(',')[7]==" 'FR Y-9C'" or str(row).split(',')[7]==" 'FR Y-9LP'" or str(row).split(',')[7]==" 'FR Y-9SP'":
				#if datetime.strptime(str(row).split(',')[2][0:str(row).split(',')[2].find(' ')].strip(),'%m/%d/%Y').strftime('%Y%m%d') <= qtr.strftime('%Y%m%d') and datetime.strptime(str(row).split(',')[3][0:str(row).split(',')[3].find(' ')].strip(),'%m/%d/%Y').strftime('%Y%m%d') >= qtr.strftime('%Y%m%d'):
				mdrm_list += [str(row).split(',')[0].strip().replace('[','').replace("'",'')+str(row).split(',')[1].strip().replace('[','').replace("'",'')]
	missing_mdrms=['BHCKHT69','BHCKJA21','BHCT2143','BHCKJA22','TEXTFT29','BHCPJJ33','BHCPHT70','BHCPHT69','TEXT5485','TEXT5486','TEXT5488','TEXT5487','TEXT5489']
	mdrm_list.extend(missing_mdrms)
	mdrm_list = set(mdrm_list)
	#print(mdrm_list)
	#sys.exit()
	#mdrm_list = list(mdrm_list)
	return mdrm_list

def reporters():
	attr_url = 'https://www.ffiec.gov/npw/FinancialReport/ReturnAttributesActiveZipFileCSV'
	npw_attr = requests.get(attr_url)
	zf = ZipFile(BytesIO(npw_attr.content))
	attr = csv.reader(zf.open('CSV_ATTRIBUTES_ACTIVE.CSV').read().decode('utf-8').split('\n'), delimiter=',')
	resp_list=[]
	for row in attr:
		if len(str(row).split(','))>1:
			if str(row).split(',')[3].strip()=="'1'" or str(row).split(',')[66].strip()=="'1'" or str(row).split(',')[-1].strip().replace(']','')=="'1'":
				resp_list += [row[0]]
	return resp_list

def getData(rssd,form):
	dict={}
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

mdrm_list=mdrms()
rssd_list=reporters()

start_time = datetime.today()

with open('npw.csv','w',newline='') as f:
	fieldnames=mdrm_list
	writer=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='raise')
	writer.writeheader()
	for id in rssd_list:
		print(id)
		dictData = {}
		try:
			sp_data = getData(id,'FRY9SP')
			dictData.update(sp_data)
		except:
			continue
		try:
			c_data = getData(id,'FRY9C')
			dictData.update(c_data)
		except:
			continue
		try:
			lp_data = getData(id,'FRY9LP')
			dictData.update(lp_data)
		except:
			continue
		if len(dictData)>0:
			writer.writerow(dictData)
print(start_time, datetime.today())