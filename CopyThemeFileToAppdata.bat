@REM @echo off
xcopy  /I "Sun-Valley-ttk-theme\sun-valley.tcl" %AppData%\KUPC\sun-valley.tcl*
xcopy /E /I Sun-Valley-ttk-theme\theme\ %AppData%\KUPC\theme\
echo 主題複製完畢
timeout /t 5 /nobreak