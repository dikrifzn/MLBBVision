from pipeline.builder import PostGameBuilder

from ocr_engine.predict import predict_text

from ocr_engine.preprocess import (
    preprocess_gold,
    preprocess_level,
    preprocess_kda,
    preprocess_name,
    preprocess_score,
    preprocess_duration,
)

from ocr_engine.parser import (
    parse_gold,
    parse_level,
    parse_kda,
    parse_name,
    parse_score,
    parse_duration,
)


class PostGamePipeline:

    def __init__(

        self,

        crop_engine,

        hero_predict,

        item_predict

    ):

        self.crop_engine = crop_engine

        self.hero_predict = hero_predict

        self.item_predict = item_predict

    # OCR

    def predict_ocr(self, crop, mode):

        if mode == "gold":

            crop = preprocess_gold(crop)

            result = predict_text(crop, "gold")

            return parse_gold(result["text"])

        elif mode == "level":

            crop = preprocess_level(crop)

            result = predict_text(crop, "level")

            return parse_level(result["text"])

        elif mode == "kda":

            crop = preprocess_kda(crop)

            result = predict_text(crop, "kda")

            return parse_kda(result["text"])

        elif mode == "name":

            crop = preprocess_name(crop)

            result = predict_text(crop, "name")

            return parse_name(result["text"])

        elif mode == "score":

            crop = preprocess_score(crop)

            result = predict_text(crop, "score")

            return parse_score(result["text"])

        elif mode == "duration":

            crop = preprocess_duration(crop)

            result = predict_text(crop, "duration")

            return parse_duration(result["text"])

        return None

    # RUN

    def run(self, image):

        crops = self.crop_engine.extract(image)

        builder = PostGameBuilder()

        for name, crop in crops.items():

            # HERO

            if name.startswith("hero"):

                builder.add(

                    name,

                    self.hero_predict(crop)

                )

            # ITEM

            elif name.startswith("item"):

                builder.add(

                    name,

                    self.item_predict(crop)

                )

            # GOLD

            elif name.startswith("gold"):

                builder.add(

                    name,

                    self.predict_ocr(crop, "gold")

                )

            # LEVEL

            elif name.startswith("level"):

                builder.add(

                    name,

                    self.predict_ocr(crop, "level")

                )

            # KDA

            elif name.startswith("kda"):

                builder.add(

                    name,

                    self.predict_ocr(crop, "kda")

                )

            # PLAYER NAME

            elif name.startswith("name"):

                builder.add(

                    name,

                    self.predict_ocr(crop, "name")

                )

            # PLAYER SCORE

            elif name.startswith("score_"):

                builder.add(

                    name,

                    self.predict_ocr(crop, "score")

                )

            # TEAM SCORE

            elif name in [

                "blue_team_score",

                "red_team_score"

            ]:

                builder.add(

                    name,

                    self.predict_ocr(crop, "score")

                )

            # MATCH DURATION

            elif name == "match_duration":

                builder.add(

                    name,

                    self.predict_ocr(crop, "duration")

                )

            # VICTORY

            elif name == "victory":

                result = predict_text(

                    preprocess_name(crop),

                    "name"

                )

                builder.add(

                    name,

                    result["text"]

                )

        return builder.build()