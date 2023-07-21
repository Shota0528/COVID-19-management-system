CREATE DATABASE if NOT EXISTS covid19;
USE covid19;

DROP TABLE if EXISTS infected;
DROP TABLE if EXISTS conduct;
DROP TABLE if EXISTS healthmanagement;
DROP TABLE if EXISTS symptoms;
DROP TABLE if EXISTS user;

CREATE TABLE user(
    userID INT NOT NULL AUTO_INCREMENT, 
    usercode VARCHAR(32) UNIQUE NOT NULL, 
    userpassword VARCHAR(32) NOT NULL, 
    facultyoffice VARCHAR(32) NOT NULL, 
    namae VARCHAR(32) NOT NULL, 
    kind VARCHAR(32) NOT NULL, 
    phone VARCHAR(32) NOT NULL, 
    email VARCHAR(32) NOT NULL, 
    adminflag BOOLEAN default FALSE, 
    lastupdate DATETIME, 
    PRIMARY KEY(userID)   
);

CREATE TABLE symptoms(
    symptomsID INT NOT NULL AUTO_INCREMENT, 
    temperature FLOAT NOT NULL, 
    jointpain BOOLEAN default FALSE, 
    washedoutfeeling BOOLEAN default FALSE, 
    headache BOOLEAN default FALSE, 
    sorethroat BOOLEAN default FALSE, 
    breathless BOOLEAN default FALSE, 
    coughsneezing BOOLEAN default FALSE, 
    nausea BOOLEAN default FALSE, 
    abdominalpain BOOLEAN default FALSE, 
    tastedisorder BOOLEAN default FALSE, 
    olfactorydisorder BOOLEAN default FALSE, 
    lastupdate DATETIME, 
    PRIMARY KEY(symptomsID)
);

CREATE TABLE healthmanagement(
    healthmanagementID INT NOT NULL AUTO_INCREMENT, 
    symptomsID INT NOT NULL, 
    userID INT NOT NULL, 
    recorddate DATE NOT NULL, 
    timezone BOOLEAN NOT NULL, 
    lastupdate DATETIME, 
    PRIMARY KEY(healthmanagementID), 
    FOREIGN KEY(symptomsID)
        REFERENCES symptoms(symptomsID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY(userID)
        REFERENCES user(userID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE conduct(
    conductID INT NOT NULL AUTO_INCREMENT, 
    userID INT NOT NULL, 
    recorddate DATE NOT NULL, 
    actiontime VARCHAR(32) NOT NULL, 
    location VARCHAR(32) NOT NULL, 
    movementmethod VARCHAR(32), 
    dtp VARCHAR(64), 
    arr VARCHAR(64),
    companionflag BOOLEAN default FALSE,  
    relationshipnum VARCHAR(64), 
    specialmention VARCHAR(1024), 
    lastupdate DATETIME, 
    PRIMARY KEY(conductID), 
    FOREIGN KEY(userID)
        REFERENCES user(userID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE infected(
    infectedID INT NOT NULL AUTO_INCREMENT, 
    userID INT NOT NULL, 
    closecontact BOOLEAN default FALSE, 
    infect BOOLEAN default FALSE, 
    attendancestop varchar(32), 
    medicalinstitutionname varchar(32), 
    doctorname varchar(32), 
    lastupdate datetime, 
    PRIMARY KEY(infectedID), 
    FOREIGN KEY(userID)
        REFERENCES user(userID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

DESC user;
DESC healthmanagement;
DESC symptoms;
DESC conduct;
DESC infected;