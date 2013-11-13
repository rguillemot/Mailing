#!/usr/bin/env bash
#./crunchbase_extractdata.py -d advertising.pkl -t div -i class -v col1_office_address -o advertising_address.pkl
./crunchbase_extractdata.py -d advertising.pkl -t a -i target -v _self -o advertising_website.pkl
