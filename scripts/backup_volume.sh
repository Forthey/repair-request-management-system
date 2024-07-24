datetime=$(date +%Y-%m-%d)
echo "---------------------------------------"
echo " "
echo "Starting database backup on ${datetime}"
echo " " 
echo "---------------------------------------"
sudo docker run --rm  --volumes-from postgres -v repair-request-management-system_pg_data:/pg_data -v /home/forthey/backup:/backup \
ubuntu tar cvf /backup/backup_$datetime.tar /pg_data
echo "---------------------------------------"
echo "Backup complete!"
echo "---------------------------------------"
