@echo off
echo Installing required Python packages...

pip install bokeh matplotlib numpy pygame pymavlink pyserial

echo Installation complete.
echo Press any key to exit...
pause > nul
