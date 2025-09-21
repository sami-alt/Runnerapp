
create table suoritukset(id integer primary key autoincrement, name text, length float, time int, comment text);

create table kayttajat(id integer primary key autoincrement, username text unique, password_hash text);