@echo off
xcopy sun-valley.tcl %AppData%\KUPC\sun-valley.tcl*
xcopy /E /I theme\ %AppData%\KUPC\theme\
echo 主題複製完畢
timeout /t 5 /nobreak