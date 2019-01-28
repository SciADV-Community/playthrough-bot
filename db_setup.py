#!python3
import sqlite3, asyncio, discord, config

# Set up the tables
def table_setup(client):
    ### Reset ###
    #client.cursor.execute("DROP TABLE IF EXISTS Config")
    #client.cursor.execute("DROP TABLE IF EXISTS Game")
    #client.cursor.execute("DROP TABLE IF EXISTS Game_Alias")
    #client.cursor.execute("DROP TABLE IF EXISTS Channel")
    #client.cursor.execute("DROP TABLE IF EXISTS Command")
    #client.cursor.execute("DROP TABLE IF EXISTS Argument")
    
    ### Tables ###
    # Table to hold details about a certain VN
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Game (
        Name VARCHAR(255) UNIQUE NOT NULL,
        Role_Name VARCHAR(255) NOT NULL,
        Progress INT(1) DEFAULT 0,
        Channel_suffix VARCHAR(255) NOT NULL,
        PRIMARY KEY(Name)
    )
    ''')
    # Table to hold the configuration for a specific server
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Config (
        Guild_ID INT UNIQUE NOT NULL,
        Guild_Name VARCHAR(255) NOT NULL,
        Chapter_prefix VARCHAR(255) DEFAULT '{0}',
        Route_prefix VARCHAR(255) DEFAULT '{1}',
        Main_Game VARCHAR(255),
        PRIMARY KEY(Guild_ID),
        FOREIGN KEY(Main_Game) REFERENCES Game(Name)
    )
    '''.format(config.ch_prefix, config.route_suffix))
    # Table to hold Game <-> Guild connections
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Game_Guild (
        Game_Name VARCHAR(255) NOT NULL,
        Guild_ID INT NOT NULL,
        Start_category INT UNIQUE,
        Archive_category INT UNIQUE,
        PRIMARY KEY(Game_Name, Guild_ID),
        FOREIGN KEY(Game_Name) REFERENCES Game(Name)
    )
    ''')
    # Table to hold alternate game aliases
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Game_Alias (
        Alias VARCHAR(255) UNIQUE NOT NULL,
        Game_Name VARCHAR(255) NOT NULL,
        PRIMARY KEY(Alias),
        FOREIGN KEY(Game_Name) REFERENCES Game(Name)
    )
    ''')
    # Table to hold information about individual playthrough channels
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Channel (
        ID INT UNIQUE NOT NULL,
        Owner INT NOT NULL,
        Guild INT NOT NULL,
        Game VARCHAR(255) NOT NULL,
        PRIMARY KEY(ID),
        FOREIGN KEY(Guild) REFERENCES Config(Guild_ID),
        FOREIGN KEY(Game) REFERENCES Game(Name)
    )
    ''')
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Command (
        Name VARCHAR(255) UNIQUE NOT NULL,
        Description TEXT NOT NULL,
        Example VARCHAR(255) NOT NULL,
        PRIMARY KEY(Name)
    )
    ''')
    client.cursor.execute('''
    CREATE TABLE IF NOT EXISTS Argument (
        Command VARCHAR(255) NOT NULL,
        Argument VARACHAR(255) NOT NULL,
        PRIMARY KEY(Command, Argument),
        FOREIGN KEY(Command) REFERENCES Command(Name)
    )
    ''')
    # Commit the changes to the database
    client.database.commit()