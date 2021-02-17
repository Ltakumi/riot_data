# riot_data
Download riot (the company) related data from their api and other sources

Created an easy to use client for the riot API to download game information for various data projects.

## Description

Tool for downloading Riot Games related data from their api and other sources.

There are 4 main composents to the pipeline :
- an api client to manage requests (if request rate are not respected key is blacklisted)
- an api manager to format requests to obtain the required information
- a player manager to find players and their games
- a game manager to find games and download them

## Usage

A demo jupyter notebooks shows the different steps for a complete database :
- finding players
- finding games for these players
- downloading said games

Since requests are limited per region, by running run.py you will be able to run the same requests on all regions in parallel.

## Parameters

The following parameters are available for modification in the config file:

- api_key : must be a valid api key, available on https://developer.riotgames.com/ if you have a riot account. Key must be recent as they expire after 24 hours
- path2db : location where databases will be stored
- path2games : location where game data will be stored

- findplayers : do we want to find players (default is true, put to false if it has already been done)
- findgames : do we want to find games (default is true, put to false if it has already been done)
- dlgames : do we want to download games (default is true, put to false if it has already been done)

- regions : region from which to download games. Default is all of them.
- high_elo_players : number of players in high elo (master and above) to find per region
- low_elo_players : number of players in lower elo (diamond and below) to find per region
- patches : list of patches to download data from. Gameinfo is available 3 years, timeline is available 1 year.

- gameinfo : Do we want game info
- timeline : Do we want the game timeline
