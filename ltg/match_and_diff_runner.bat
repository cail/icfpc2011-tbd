@echo off

if %1 == 1 goto RUN_SLAVE
python src/play.py --replay match_and_diff_our.rpl --maxturns 1000 "ZombieRush()" "None" 0
goto END

:RUN_SLAVE
python src/play.py "None" "ZombieRush()" 1
:END
