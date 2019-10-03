import pandas as pd
import numpy as np
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import Helper_Functions as hf
import re
import time
from sqlalchemy import create_engine

#////PROGRAM PARAMETERS////
wk_dir ='C:\\Users\\Adam Durrett\\Documents\\GitHub\\sentiment_analysis\\Data\\'

engine = create_engine("mysql+pymysql://LOLread:"+'LaberLabsLOLquery'+"@lolsql.stat.ncsu.edu/lol")
champions = pd.read_sql('select name from champions', engine)


# 'Jax' 'Sona' 'Tristana' 'Varus' "Kai'Sa" 'Fiora' 'Singed' 'Tahm Kench'
#  'LeBlanc' 'Thresh' 'Karma' 'Jhin' 'Rumble' 'Udyr' 'Lee Sin' 'Yorick'
#  'Ornn' 'Kayn' 'Kassadin' 'Sivir' 'Miss Fortune' 'Draven' 'Yasuo' 'Kayle'
#  'Shaco' 'Renekton' 'Hecarim' 'Fizz' "Kog'Maw" 'Maokai' 'Lissandra' 'Jinx'
#  'Urgot' 'Fiddlesticks' 'Galio' 'Pantheon' 'Talon' 'Gangplank' 'Ezreal'
#  'Gnar' 'Teemo' 'Annie' 'Mordekaiser' 'Azir' 'Kennen' 'Riven' "Cho'Gath"
#  'Aatrox' 'Poppy' 'Taliyah' 'Illaoi' 'Heimerdinger' 'Alistar' 'Xin Zhao'
#  'Lucian' 'Volibear' 'Sejuani' 'Nidalee' 'Garen' 'Leona' 'Zed'
#  'Blitzcrank' 'Rammus' "Vel'Koz" 'Caitlyn' 'Trundle' 'Kindred' 'Quinn'
#  'Ekko' 'Nami' 'Swain' 'Taric' 'Syndra' 'Rakan' 'Skarner' 'Braum' 'Veigar'
#  'Xerath' 'Corki' 'Nautilus' 'Ahri' 'Jayce' 'Darius' 'Tryndamere' 'Janna'
#  'Elise' 'Vayne' 'Brand' 'Zoe' 'Graves' 'Soraka' 'Xayah' 'Karthus'
#  'Vladimir' 'Zilean' 'Katarina' 'Shyvana' 'Warwick' 'Ziggs' 'Kled'
#  "Kha'Zix" 'Olaf' 'Twisted Fate' 'Nunu' 'Rengar' 'Bard' 'Irelia' 'Ivern'
#  'Wukong' 'Ashe' 'Kalista' 'Akali' 'Vi' 'Amumu' 'Lulu' 'Morgana'
#  'Nocturne' 'Diana' 'Aurelion Sol' 'Zyra' 'Viktor' 'Cassiopeia' 'Nasus'
#  'Twitch' 'Dr. Mundo' 'Orianna' 'Evelynn' "Rek'Sai" 'Lux' 'Sion' 'Camille'
#  'Master Yi' 'Ryze' 'Malphite' 'Anivia' 'Shen' 'Jarvan IV' 'Malzahar'
#  'Zac' 'Gragas'
related_words = ["League of Legends", "jungler", "normals", "ranked", "ARAM", "urf", "penta kill", "Summoner",
                 "summoner's rift", "Howling Abyss", "mage", "tradeplayz", "mastery", "inspiration", "buffed", "nerfed",
                 "dyrus", "pbe", "drgn", "toxic", "cc", "jg", "void", "assassin", "supporting", "moobeat", "bronze",
                 "silver", "gold", "platinum", "plat", "diamond", "masters", "master", "challenger", "skt", "champion",
                 "crit", "strike", "report", "elo", "legendary", "duo", "solo", "queue", "flex", "push", "ward", "farm",
                 "cast", "flash", "smite", "teleport", "ignite", "jungle", "top", "mid", "support", "supp", "buff",
                 "nerf", "force", "conqueror", "lolesports", "lvl", "nalcs", "lcs", "winrate", "kda", "ultimate",
                 "fighter", "marksman", "adc", "lane", "champ", "chat", "dragon", "meta", "riot", "wins", "tank",
                 "squishy", "ap", "ability", "power", "attack", "damage", "ad", "leagueoflegends", "legends", "league"]

#[[Problem words],[related words]]
unrelated_words = ["Trump", "Bernie", "Hillary", "Obama", "Fake news", "CNN", "WWE", "Ed Sheeran", "Fortnite_Br",
                   "president","Black Panther", "wakanda", "Tumblr", "Politicians", "Democracy", "trans", "alexa",
                   "editor", "usa", "armys","awards", "judge", "language", "gym", "changing", "science", "chocolate",
                   "elise_christie", "beer", "nature","cross", "society", "conference", "pubg", "research",
                   "papaporter1", "speech", "commission", "taylor","wine", "registration", "outfit", "makeup", "faith",
                   "realdonaldtrump", "county", "marketing", "r95731", "crime", "church", "jackson" , "kim", "kevin",
                   "national", "lies", "married", "girlfriend", "driving", "ps4", "asuka", "mtvbrkpopbts", "rihanna",
                   "facebook", "apple", "bucks", "healthcare", "panther", "husband","prince", "FL", "heroldbarton",
                   "jordan", "hungary", "romance", "putin", "york", "olympics", "basketball","playstation",
                   "government", "boyfriend", "johnson", "fortnite", "wrestlemania", "instagram", "btsarmy",
                   "iheartawards", "weather", "SOA", "florida"]
