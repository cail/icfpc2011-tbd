git -c core.eol=lf -c core.autocrlf=false archive -v --format=tar -o submission.tar HEAD src install run && gzip -f submission.tar
