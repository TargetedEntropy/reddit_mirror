# Reddit image to Discord Mirror

This is used to mirror your favorite [subreddits](https://reddit.com) to [Discord](https://discord.com) channels. it supports multiple subreddits being sent to different channels, or servers.  You only need to provide the API access to Reddit, Discord and specify the Discord Channel ID.  The bot can be invited to multiple servers and will mirror i.redd.it images to imgur.


## Requirements

* [Reddit API Access](https://www.reddit.com/prefs/apps/)
* [Discord Bot Token](https://discord.com/developers/applications)
* [Imgur Client ID](https://api.imgur.com/oauth2/addclient)

## Installation

* Install MySQL
* Create a MySQL Database & User
* Create the MySQL table
* Add python modules


## Configuration
* Create your .env file
    * `cp env.sample .env`
* Configure .env to populate examples
* Add your Discord/Reddit/Imgur Credentials
* Setup the subreddits and channel destinations in `main.py`
    ```python
        SUBREDDITS = [
            {"name": "pics", "channel_id": 1011474405368797184},
            {"name": "space", "channel_id": 1011788355237578285}
        ]
    ```


## Create a SQL Database & User
```sql
CREATE DATABASE DATABASE_NAME;
CREATE USER 'USERNAME_STRING'@'localhost' IDENTIFIED BY 'PASSWORD_STRING';
SET PASSWORD FOR 'USERNAME_STRING'@'localhost' = PASSWORD('PASSWORD_STRING');
GRANT ALL PRIVILEGES ON DATABASE_NAME.*  TO 'USERNAME_STRING'@'localhost';
```

## SQL Table structure
```sql
CREATE TABLE `subreddit_posts` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`post_id` VARCHAR(24),
	`post_title` TEXT,
	`post_url` TEXT,
	`subreddit_name` VARCHAR(250),
	`post_datetime` DATETIME,
	PRIMARY KEY (`id`)
);
```
