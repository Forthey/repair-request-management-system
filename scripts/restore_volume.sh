datetime=$(date +%Y-%m-%d)
echo "---------------------------------------"
echo " "
echo "Starting database restore on ${datetime}, from archive $1"
echo " "
echo "---------------------------------------"
docker run --rm  -v repair-request-management-system_pg_data:/pg_data -v /home/forthey/backup:/backup ubuntu  tar xvf /backup/$1 -C /pg_data --strip 1
echo "---------------------------------------"
echo "Backup complete!"
echo "---------------------------------------"
