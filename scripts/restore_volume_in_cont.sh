datetime=$(date +%Y-%m-%d)
echo "---------------------------------------"
echo " "
echo "Starting database restore on ${datetime}, from archive $1"
echo " "
echo "---------------------------------------"
tar xvf /backup/$1 -C /pg_data --strip 1
echo "---------------------------------------"
echo "Restore complete!"
echo "---------------------------------------"
