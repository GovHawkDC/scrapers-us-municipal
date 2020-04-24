# Catch ctrl-c
trap "echo Exited!; exit;" SIGINT SIGTERM

for f in *; do
    if [ -d "$f" ]; then
       echo "$f"
       pupa update $f events --scrape
    fi
done