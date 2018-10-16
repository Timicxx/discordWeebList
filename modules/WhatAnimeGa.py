import requests
import base64
import uuid
from PIL import Image
from asyncio import sleep
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import quote


class HelperFunctions:
    def __init__(self):
        self.extentions = [".png", ".jpg", ".jpeg", ".gif"]

    def verifyUrl(self, url):
        val = URLValidator()
        try:
            val(url)
            return True
        except ValidationError:
            return False

    def convertImageToBase64(self, image_path):
        if self.verifyUrl(image_path) is False:
            return None
        temp_image_path = ""
        for extention in self.extentions:
            if image_path.endswith(extention):
                temp_image_path = "helper/images/{}".format(str(uuid.uuid4()) + extention)
                break
        if temp_image_path == "":
            return None
        with open(temp_image_path, 'wb') as saved_image:
            response = requests.get(image_path, stream=True)
            saved_image.write(response.content)
        img = Image.open(temp_image_path)
        w_size = int(round(img.size[0] * 0.5))
        h_size = int(round(img.size[1] * 0.5))
        img = img.resize((w_size, h_size), Image.ANTIALIAS)
        img.save(temp_image_path)
        encoded = base64.b64encode(open(temp_image_path, "rb").read())
        return encoded

    def getPreview(self, json):
        preview = (
            "https://whatanime.ga/preview.php?"
            "anilist_id={}&"
            "file={}&"
            "t={}&"
            "token={}"
        ).format(
            str(json["docs"][0]["anilist_id"]),
            quote(json["docs"][0]["filename"]),
            str(json["docs"][0]["at"]),
            json["docs"][0]["tokenthumb"]
        )

        vid = requests.get(preview, stream=True)
        mp4_path = "helper/videos/{}.mp4".format(str(uuid.uuid4()))
        with open(mp4_path, 'wb') as mp4_out:
            mp4_out.write(vid.content)

        return mp4_path


class WhatAnimeGa:
    def __init__(self, TOKEN, BOT):
        self.bot = BOT
        self.helper = HelperFunctions()
        self.token = TOKEN
        self.urls = {
            "me": "https://whatanime.ga/api/me?token={}".format(self.token),
            "search": "https://whatanime.ga/api/search?token={}".format(self.token),
        }

    def initialize(self):
        response = requests.get(self.urls["me"])
        return response.json()

    def getSourceFromImage(self, image_path):
        encoded = self.helper.convertImageToBase64(image_path)
        if encoded is None:
            return None
        data = {
            'image': encoded,
        }
        response = requests.post(self.urls["search"], data=data)
        if response is None:
            return -1
        return response.json()
	
    async def getSource(self, ctx):
        '''Gets source of the image'''

        await sleep(0.5)
        await self.bot.delete_message(ctx.message)
        link = ctx.message.content
        link = link.split(' ')[1]
        source_json = self.getSourceFromImage(link)
        if source_json is None:
            msg = await self.bot.send_message(ctx.message.channel, ":x: :anger: Invalid link :anger: :x:")
            await sleep(5.0)
            await self.bot.delete_message(msg)
            return
        message = (
            "The anime is {}\n"
            "<https://anilist.co/anime/{}>\n"
            "Similariy: {}%\n"
        ).format(
            source_json["docs"][0]["title_romaji"],
            source_json["docs"][0]["anilist_id"],
            round(source_json["docs"][0]["similarity"] * 100),
            source_json["quota"]
        )

        mp4 = self.helper.getPreview(source_json)
        msg = await self.bot.send_file(ctx.message.channel, mp4, content=message)
