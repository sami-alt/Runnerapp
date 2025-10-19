
create table users(id integer primary key autoincrement, username text unique, password_hash text);

create table runs(run_id integer primary key autoincrement, name text, length float, time int,comment text,runner_id integer references users(id));

create table comments(comment_id integer primary key autoincrement, comment_creator integer references users(id), run_id integer references runs on delete cascade, comment text);

create table runSituation(situation_id integer primary key autoincrement, situation text, run_id integer references runs on delete cascade);

create table types(id integer primary key autoincrement, method text);
 
create table run_in_types(id integer primary key, run_id integer references runs on delete cascade, type_id integer references types);

create table maps(map_id integer primary key autoincrement, run_id integer references runs on delete cascade, owner_id integer references users(id), image BLOB);

create table profile_pictures(picture_id integer primary key autoincrement, image BLOB, owner_id integer references users(id))