ltg.win32.exe -silent false match "match_and_diff_runner.bat" "match_and_diff_runner.bat" 2>match_and_diff_their.log
python src/replay_to_log.py match_and_diff_our.rpl
python src/resub.py -i zero 0 match_and_diff_their.log match_and_diff_our.log
diff match_and_diff_our.log match_and_diff_their.log >match_and_diff.diff
