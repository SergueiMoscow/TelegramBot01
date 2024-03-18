#!/bin/bash

if [[ -f "/backup/telegram01.bk" && ! -f "/backup/database.txt" ]]; then
    psql -U postgres -d telegram01 < /backup/telegram01.bk
    if [[ $? -eq 0 ]]; then
        echo "Database restore was successful"
        date > /backup/database.txt
    else
        echo "Database restore failed - check the logs for details"
    fi
fi

exec "$@"
