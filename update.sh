#!/bin/sh

# Clone or pull COVID-19 repo
if ls COVID-19
then
    echo "Pulling from COVID-19 repo..."
    cd COVID-19
    git pull
    cd ..
else
    echo "Cloning COVID-19 repo..."
    git clone https://github.com/CSSEGISandData/COVID-19.git
fi

# Clean up
echo "Removing data.csv and png/*..."
rm data.csv
rm -f png/*

# Generate new data and plots
echo "Calling python script to generate new data.csv and plots..."
python kovid.py
