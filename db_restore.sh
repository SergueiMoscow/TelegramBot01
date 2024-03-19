#!/bin/bash
# это пример подгрузки данных. В докере выключен. Добавлять вручную
if [[ -f "/app/backup/telegram01.bk" && ! -f "/app/backup/database.txt" ]]; then
    psql -U postgres -d telegram01 < /backup/telegram01.bk
    if [[ $? -eq 0 ]]; then
        echo "Database restore was successful"
        date > /app/backup/database.txt
    else
        echo "Database restore failed - check the logs for details"
    fi
fi

exec "$@"
