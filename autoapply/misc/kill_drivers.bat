@echo off
rem   just kills stray local chromedriver.exe instances.
rem   useful if you are trying to clean your project, and your ide is complaining.

taskkill /IM MicrosoftWebDriver.exe /F
taskkill /IM chromedriver.exe /F