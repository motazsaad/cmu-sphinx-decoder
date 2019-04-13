read YYYY MM DD <<<$(date +'%Y %m %d')
echo "today"
echo $YYYY/$MM/$DD
yesterday=$(date -d "yesterday" '+%Y/%m/%d')
echo "yesterday"
echo $yesterday

# https://crontab.guru/every-day-at-1am

