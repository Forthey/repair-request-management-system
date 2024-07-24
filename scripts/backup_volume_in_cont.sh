datetime=$(date +%Y-%m-%d)
echo "---------------------------------------"
echo " "
echo "Starting database backup on ${datetime}"
echo " " 
echo "---------------------------------------"
tar cvf /backup/backup_$datetime.tar /pg_data
echo "---------------------------------------"
echo "Backup complete!"
echo "---------------------------------------"
