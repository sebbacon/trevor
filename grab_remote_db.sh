dropdb -p 5433 trevor
createdb -p 5433 -O trevor trevor
ssh seb 'su -c "/usr/lib/postgresql/8.4/bin/pg_dump -p 5433 trevor" postgres' | sed -e 's/whatevertrevor.co.uk/localhost:8010/g' | psql -p 5433 trevor 
