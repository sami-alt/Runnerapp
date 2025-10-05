
create table runs(run_id integer primary key autoincrement, name text, length float, time int, guest_comment text ,comment text,runner_id integer references users);

create table users(id integer primary key autoincrement, username text unique, password_hash text);