mysqldump -u root -p pypykids --single-transaction --quick --lock-tables=false > ./backup/db1-backup-$(date +%F).sql
