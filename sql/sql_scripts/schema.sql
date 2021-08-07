DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS func;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS solutions;

CREATE TABLE user (
  id INT AUTO_INCREMENT,
  lev INT NOT NULL,
  token TEXT,
  tmp_token TEXT,
  solves INT,
  first_name TEXT,
  last_name TEXT,
  other TEXT,
  PRIMARY KEY (id)
);

CREATE TABLE events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  challenge INT NOT NULL,
  fcn_name TEXT,
  event TEXT
);

CREATE TABLE func (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  old_name TEXT,
  new_name TEXT,
  challenge INT NOT NULL
);

CREATE TABLE notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    challenge INT NOT NULL,
    note TEXT
);

CREATE TABLE solutions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    challenge INT NOT NULL,
    solution TEXT
);
