import datetime

def date_calculator(month,year,add):
	if int((month + add)/12)>0:
		year+=int((month + add)/12)

	return datetime.datetime(year=year,month=(month+add)%12,day=1)