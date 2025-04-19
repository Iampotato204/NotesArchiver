-- drop table if exists notes;
-- create table notes(
-- id bigint unsigned auto_increment primary key unique,
-- tgid bigint unsigned default 0,
-- _time bigint unsigned default unix_timestamp(),
-- _group int default 0, /*potential to create groups table*/
-- file longblob,
-- filename varchar(2048) default "_",
-- caption varchar(4096) default "", /*caption caps at 1024 (2048 with premium), but we are trying to push normal text into caption*/
-- extention varchar(500) default "txt"
-- );

drop table if exists notes;
create table notes(
id bigint unsigned auto_increment primary key unique,
uid bigint unsigned default 0,
_type int default 1,
_group int default 0
);
drop table if exists note_text;
create table note_text(
name varchar(512),
id bigint unsigned auto_increment primary key unique,
tgid bigint unsigned default 0,
_time bigint unsigned default unix_timestamp(),
text varchar(4096)
);
drop table if exists note_file;
create table note_file(
name varchar(512),
id bigint unsigned auto_increment primary key unique,
tgid bigint unsigned default 0,
_time bigint unsigned default unix_timestamp(),
file longblob,
filename varchar(2048) default "_",
text varchar(2048) default "",
extention varchar(500) default "txt"
);
drop table if exists users;
create table users(
tgid bigint unsigned,
status int default 0
);

-- this works
-- select * from (select 1 as retid) a;
-- this doesnt... why?
-- select * from (insert into note_text(text) values ("hello") returning id as retid) b;
-- in this case i dont need id for note_*

-- insert into note_file(tgid) values (15);
-- insert into notes(_type,_group,uid) select 1,max(id),max(id) from note_text;
-- insert into notes(_type,_group,uid) select 2,max(id),max(id) from note_file;
-- select "notes";
-- select * from notes;
-- select "note_text";
-- select * from note_text;
-- select "note_file";
-- select * from note_file;
