
origdata := $(wildcard COVID-19/csse_covid_19_data/*.csv)
plotfiles := $(wildcard png/*.png)

figures: $(plotfiles)
	python kovid.py --plot

data.csv: $(origdata)
	cd COVID-19 && git pull
	python kovid.py --data
