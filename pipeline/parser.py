import re


class ROIParser:

    # HERO

    HERO_PATTERN = re.compile(
        r"hero_(blue|red)_(\d+)"
    )

    # ITEM

    ITEM_PATTERN = re.compile(
        r"item(\d+)_(blue|red)_(\d+)"
    )

    # GOLD

    GOLD_PATTERN = re.compile(
        r"gold_(blue|red)_(\d+)"
    )

    # LEVEL

    LEVEL_PATTERN = re.compile(
        r"level_(blue|red)_(\d+)"
    )

    # KDA

    KDA_PATTERN = re.compile(
        r"kda_(blue|red)_(\d+)"
    )

    # PLAYER NAME

    NAME_PATTERN = re.compile(
        r"name_(blue|red)_(\d+)"
    )

    # PLAYER SCORE

    PLAYER_SCORE_PATTERN = re.compile(
        r"score_(blue|red)_(\d+)"
    )

    # TEAM SCORE

    TEAM_SCORE_PATTERN = re.compile(
        r"(blue|red)_team_score"
    )

    # MATCH DURATION

    MATCH_DURATION_PATTERN = re.compile(
        r"match_duration"
    )

    # VICTORY

    VICTORY_PATTERN = re.compile(
        r"victory"
    )

    # PARSER

    @staticmethod
    def parse(name):

        hero = ROIParser.HERO_PATTERN.fullmatch(name)

        if hero:

            return {

                "type": "hero",

                "team": hero.group(1),

                "player": int(hero.group(2))

            }

        item = ROIParser.ITEM_PATTERN.fullmatch(name)

        if item:

            return {

                "type": "item",

                "slot": int(item.group(1)),

                "team": item.group(2),

                "player": int(item.group(3))

            }

        gold = ROIParser.GOLD_PATTERN.fullmatch(name)

        if gold:

            return {

                "type": "gold",

                "team": gold.group(1),

                "player": int(gold.group(2))

            }

        level = ROIParser.LEVEL_PATTERN.fullmatch(name)

        if level:

            return {

                "type": "level",

                "team": level.group(1),

                "player": int(level.group(2))

            }

        kda = ROIParser.KDA_PATTERN.fullmatch(name)

        if kda:

            return {

                "type": "kda",

                "team": kda.group(1),

                "player": int(kda.group(2))

            }

        player_name = ROIParser.NAME_PATTERN.fullmatch(name)

        if player_name:

            return {

                "type": "name",

                "team": player_name.group(1),

                "player": int(player_name.group(2))

            }

        player_score = ROIParser.PLAYER_SCORE_PATTERN.fullmatch(name)

        if player_score:

            return {

                "type": "player_score",

                "team": player_score.group(1),

                "player": int(player_score.group(2))

            }

        team_score = ROIParser.TEAM_SCORE_PATTERN.fullmatch(name)

        if team_score:

            return {

                "type": "team_score",

                "team": team_score.group(1)

            }

        duration = ROIParser.MATCH_DURATION_PATTERN.fullmatch(name)

        if duration:

            return {

                "type": "duration"

            }

        victory = ROIParser.VICTORY_PATTERN.fullmatch(name)

        if victory:

            return {

                "type": "victory"

            }

        return None