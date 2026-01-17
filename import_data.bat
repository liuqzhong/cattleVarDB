@echo off
REM Cattle SNP Database - Data Import Script
REM Make sure to run this from the project root directory

py -3.13 backend/import_data.py %*
