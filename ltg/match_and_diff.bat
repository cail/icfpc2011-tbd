ltg.win32.exe -silent false match "run_record.bat" "run_limited.bat" 2>their.log
python src/replay_to_log.py our.rpl
python src/resub.py -i zero 0 their.log our.log
diff our.log their.log >diff_our_their
