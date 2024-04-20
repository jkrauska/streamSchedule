import random

baseball_verbs = [
    "pitch", "throw", "catch", "hit", "run", "slide", "steal",
    "swing", "bunt", "field", "tag", "walk", "strike out",
    "foul", "score", "bat", "lead off", "warm up", "relieve",
    "save", "close", "coach", "manage", "train", "draft",
    "sign", "trade", "cheer", "practice", "jog", "sprint",
    "dive", "toss", "umpire", "call", "appeal", "challenge",
    "review", "celebrate", "dominate", "compete", "win",
    "lose", "tie", "bench", "play", "participate"
]

baseball_mascots = [
    "Ace",                   # Toronto Blue Jays
    "Baxter",     # Arizona Diamondbacks
    "Bernie",         # Milwaukee Brewers
    "Billy",      # Miami Marlins
    "Blooper",               # Atlanta Braves
    "Captain",               # Texas Rangers
    "Clark",                 # Chicago Cubs
    "Dinger",                # Colorado Rockies
    "Fredbird",              # St. Louis Cardinals
    "Gapper",                # Cincinnati Reds
    "Lou Seal",              # San Francisco Giants
    "MarinerMoose",         # Seattle Mariners
    "Mr. Met",               # New York Mets
    "Orbit",                 # Houston Astros
    "Paws",                  # Detroit Tigers
    "PirateParrot",         # Pittsburgh Pirates
    "RallyMonkey",          # Los Angeles Angels
    "Raymond",               # Tampa Bay Rays
    "RosieRed",             # Cincinnati Reds
    "Screech",               # Washington Nationals
    "Slider",                # Cleveland Guardians (formerly Indians)
    "Southpaw",              # Chicago White Sox
    "Stomper",               # Oakland Athletics
    "SwingingFriar",        # San Diego Padres
    "TCBear",               # Minnesota Twins
    "The Phillie Phanatic",  # Philadelphia Phillies
    "Wally", # Boston Red Sox
]


def generate_name():
    name = random.choice(baseball_mascots)
    verb = random.choice(baseball_verbs)
    return f"{name}_{verb}"