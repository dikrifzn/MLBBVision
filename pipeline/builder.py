from pipeline.parser import ROIParser


class PostGameBuilder:

    # INIT

    def __init__(self):

        self.data = {

            "game_duration": "",

            "game_number": "",

            "winmatches": "",

            "teamdata": {

                "blueteam": self._create_team("BLUE TEAM"),

                "redteam": self._create_team("RED TEAM")

            }

        }

    # TEAM

    def _create_team(self, name):

        return {

            "teamname": name,

            "score": "",

            "logo": "",

            "totalgold": 0,

            "turret": 0,

            "lord": 0,

            "turtle": 0,

            "playerlist": [

                self._create_player()

                for _ in range(5)

            ]

        }

    # PLAYER

    def _create_player(self):

        return {

            "name": "",

            "hero": "",

            "level": "",

            "KDA": "",

            "gold": 0,

            "score": "",

            "spell": "",

            "banhero": "",

            "itemlist": [

                None,
                None,
                None,
                None,
                None,
                None

            ],

            "lane": ""

        }

    # ADD DATA

    def add(self, roi_name, value):

        info = ROIParser.parse(roi_name)

        if info is None:
            return

        # GAME DURATION

        if info["type"] == "duration":

            self.data["game_duration"] = value

            return

        # VICTORY

        if info["type"] == "victory":

            text = str(value).upper()

            if "VICTORY" in text:

                self.data["winmatches"] = "blue"

            elif "DEFEAT" in text:

                self.data["winmatches"] = "red"

            return

        # TEAM

        team = "blueteam"

        if info["team"] == "red":

            team = "redteam"

        # TEAM SCORE

        if info["type"] == "team_score":

            self.data["teamdata"][team]["score"] = value

            return

        # PLAYER

        player = info["player"] - 1

        obj = self.data["teamdata"][team]["playerlist"][player]
    
        # HERO

        if info["type"] == "hero":

            obj["hero"] = value["hero"]

        # ITEM

        elif info["type"] == "item":

            slot = info["slot"] - 1

            obj["itemlist"][slot] = value["item"]

        # GOLD

        elif info["type"] == "gold":

            try:

                obj["gold"] = int(value)

            except:

                obj["gold"] = 0

        # LEVEL

        elif info["type"] == "level":

            obj["level"] = str(value)

        # KDA

        elif info["type"] == "kda":

            obj["KDA"] = str(value)

        # PLAYER NAME

        elif info["type"] == "name":

            obj["name"] = str(value)

        # PLAYER SCORE

        elif info["type"] == "player_score":

            obj["score"] = str(value)

    # CALCULATE TOTAL GOLD

    def calculate_total_gold(self):

        for team in [

            "blueteam",

            "redteam"

        ]:

            total = 0

            players = self.data["teamdata"][team]["playerlist"]

            for player in players:

                try:

                    total += int(player["gold"])

                except Exception:

                    pass

            self.data["teamdata"][team]["totalgold"] = total

    # SORT PLAYER (OPTIONAL)

    def sort_players(self):

        """
        Jika suatu saat ingin mengurutkan player
        berdasarkan lane atau score bisa dilakukan di sini.
        """

        return

    # BUILD

    def build(self):

        self.calculate_total_gold()

        self.sort_players()

        return self.data