#!/bin/bash
clear;
rm output.txt;
python Main.py >> output.txt;
cat output.txt | head --lines=50;
