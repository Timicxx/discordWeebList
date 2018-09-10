
timeout_time = 10.0


class Status:
    def __init__(self, status_name, channel_id):
        self.status_name = status_name
        self.channel_id = channel_id

    def __repr__(self):
        return self.status_name


anime_status_list = {
    "Watching": Status("Watching", 488374192023142450),
    "Dropped": Status("Dropped", 488374347061395466),
    "Plan To Watch": Status("Plan To Watch", 488374396042477589),
    "Finished": Status("Finished", 488374580176748574),
    "Hentai": Status("Hentai", 488374314517790720)
}

manga_status_list = {
    "Reading": Status("Reading", 0),
    "On Hold": Status("On Hold", 0),
    "Dropped": Status("Dropped", 0),
    "Plan To Read": Status("Plan To Read", 0),
    "Finished": Status("Finished", 0),
    "Rereading": Status("Rereading", 0)
}


class Anime:
    def __init__(self, id, title, synonyms, status, last_episode, url, thumbnail):
        self.id = id
        self.title = title
        self.synonyms = synonyms
        self.status = status
        self.current_episode = 0
        self.last_episode = last_episode
        self.score = 0.0
        self.url = url
        self.thumbnail = thumbnail
        self.message = None

    def set_title(self, title):
        self.title = title

    def set_message(self, ctx):
        self.message = ctx

    def set_status(self, status):
        self.status = status

    def set_current_episode(self, current_episode):
        self.current_episode = current_episode

    def set_last_episode(self, last_episode):
        self.last_episode = last_episode

    def set_score(self, score):
        self.score = score


class Manga:
    def __init__(self, id, title, synonyms, status, last_chapter, url, thumbnail):
        self.id = id
        self.title = title
        self.synonyms = synonyms
        self.status = status
        self.current_chapter = 0
        self.last_chapter = last_chapter
        self.score = 0.0
        self.url = url
        self.thumbnail = thumbnail
        self.message = None

    def set_title(self, title):
        self.title = title

    def set_message(self, ctx):
        self.message = ctx

    def set_status(self, status):
        self.status = status

    def set_current_chapter(self, current_chapter):
        self.current_chapter = current_chapter

    def set_last_chapter(self, last_chapter):
        self.last_chapter = last_chapter

    def set_score(self, score):
        self.score = score


import discord
import pickle
import datetime
import json
import os
import re
import requests
from discord.ext import commands
from asyncio import sleep
from shutil import copyfile


class Manager:
    def __init__(self, anime_manager, manga_manager):
        self.anime_manager = anime_manager
        self.manga_manager = manga_manager

    async def anime(self, ctx):
        '''Anime Menu'''

        options = ("[1] Add a new anime to the list\n"
                   "[2] Edit an existing anime in the list\n"
                   "[3] Remove an existing anime in the list\n"
        )
        message = (
            "```js\n"
            "Please select one of the options.\n"
            "\n"
            "{}"
            "\n"
            "Type the number for the option you would like to select.\n"
            "Type 'cancel' to cancel the operation.\n"
            "```\n"
        ).format(options)

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "1":
            await bot.delete_message(response)
            await self.anime_manager.add(ctx)
        elif response.content == "2":
            await bot.delete_message(response)
            await self.anime_manager.edit(ctx)
        elif response.content == "3":
            await bot.delete_message(response)
            await self.anime_manager.remove(ctx)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        return

    async def manga(self, ctx):
        '''Manga Menu'''

        options = ("[1] Add a new manga to the list\n"
                   "[2] Edit an existing manga in the list\n"
                   "[3] Remove an existing manga in the list\n"
                   )
        message = (
            "```js\n"
            "Please select one of the options.\n"
            "\n"
            "{}"
            "\n"
            "Type the number for the option you would like to select.\n"
            "Type 'cancel' to cancel the operation.\n"
            "```\n"
        ).format(options)

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "1":
            await bot.delete_message(response)
            await self.manga_manager.add(ctx)
        elif response.content == "2":
            await bot.delete_message(response)
            await self.manga_manager.edit(ctx)
        elif response.content == "3":
            await bot.delete_message(response)
            await self.manga_manager.remove(ctx)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        return


class AnimeManager:
    def __init__(self, status_list):
        self.status_list = status_list
        self.anime_list = {}
    
    async def add(self, ctx):
        '''Adds an anime to the list'''

        message = (
            "```js\n"
            "Please type the name of the anime to add.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)

            query = '''
            query ($id: Int, $page: Int, $perPage: Int, $search: String) {
                Page (page: $page, perPage: $perPage) {
                    pageInfo {
                        total
                        currentPage
                        perPage
                    }
                    media (id: $id, type: ANIME, search: $search) {
                        id
                        type
                        title {
                            romaji
                            english
                        }
                        episodes
                        synonyms
                        coverImage {
                            large
                        }
                        siteUrl
                    }
                }
            }
            '''
            variables = {
                'search': response.content,
                'page': 1,
                'perPage': 5
            }
            url = 'https://graphql.anilist.co'

            anilist_response = requests.post(url, json={'query': query, 'variables': variables})
            data = anilist_response.json()
            data = data["data"]["Page"]

            entries = ""
            for i, anime_entry in enumerate(data["media"]):
                entries += "[{}] {}\n".format(i + 1, anime_entry["title"]["romaji"])

            if entries == "":
                message = ":o: | Could not find any anime with that title | :o:"
                msg = await bot.send_message(ctx.message.channel, message)
                await sleep(timeout_time)
                await bot.delete_message(msg)
                return
            message = (
                "```js\n"
                "Please select the anime you would like to add to the list.\n"
                "\n"
                "{}"
                "\n"
                "Type the number for the option you would like to select.\n"
                "Type 'cancel' to cancel the operation.\n"
                "```"
            ).format(entries)

            msg = await bot.send_message(ctx.message.channel, message)
            response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
            await bot.delete_message(msg)

            if response is None:
                msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
            elif response.content == "cancel":
                await bot.delete_message(response)
            else:
                await bot.delete_message(response)
                try:
                    anime_entry_index = int(response.content) - 1
                    if anime_entry_index + 1 > data["pageInfo"]["total"]:
                        raise ValueError('Value Too High')

                    new_anime_json = data["media"][anime_entry_index]

                    synonyms = new_anime_json["synonyms"]
                    synonyms.append(new_anime_json["title"]["english"])
                    synonyms = [x for x in synonyms if x is not None]

                    new_anime = Anime(
                        new_anime_json["id"],
                        new_anime_json["title"]["romaji"],
                        synonyms,
                        self.status_list["Plan To Watch"],
                        new_anime_json["episodes"],
                        new_anime_json["siteUrl"],
                        new_anime_json["coverImage"]["large"]
                    )
                    self.anime_list[new_anime_json["id"]] = new_anime

                    embed = await self.modify_embed(self.anime_list[new_anime_json["id"]])
                    channel = bot.get_channel(str(self.status_list["Plan To Watch"].channel_id))
                    msg = await bot.send_message(
                        channel,
                        ' ',
                        embed=embed
                    )
                    self.anime_list[new_anime_json["id"]].set_message(msg)
                except ValueError:
                    await bot.delete_message(response)
                    msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                    await sleep(timeout_time)
                    await bot.delete_message(msg)
        return

    async def edit(self, ctx):
        '''Edits an anime on the list'''

        message = (
            "```js\n"
            "Please type the name of the anime to edit.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)

            entries = ""
            tags = response.content.split(' ')
            entry_index = 0
            matching_anime = []
            for key, value in self.anime_list.items():
                entry_index += 1
                for tag in tags:
                    if self.anime_list[key].title.lower().find(tag.lower()) is not -1:
                        entries += "[{}] {}\n".format(entry_index, self.anime_list[key].title)
                        matching_anime.append(key)

            if entries == "":
                message = ":o: | Could not find any anime with that title | :o:"
                msg = await bot.send_message(ctx.message.channel, message)
                await sleep(timeout_time)
                await bot.delete_message(msg)
                return

            message = (
                "```js\n"
                "Please choose one of these entries\n"
                "\n"
                "{}"
                "\n"
                "Type 'cancel' to cancel the operation.\n"
                "```"
            ).format(entries)

            msg = await bot.send_message(ctx.message.channel, message)
            response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
            await bot.delete_message(msg)

            if response is None:
                msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
            elif response.content == "cancel":
                await bot.delete_message(response)
            else:
                await bot.delete_message(response)
                try:
                    option = int(response.content)
                    if option > entry_index:
                        raise ValueError("Option does not exist")
                    anime_to_edit_index = matching_anime[option - 1]

                    options = (
                        "[1] Title\n"
                        "[2] Status\n"
                        "[3] Current episode\n"
                        "[4] Last episode\n"
                        "[5] Score\n"
                        "[6] Tags\n"
                    )
                    message = (
                        "```js\n"
                        "Please select one of the options.\n"
                        "\n"
                        "{}"
                        "\n"
                        "Type the number for the option you would like to select.\n"
                        "Type 'cancel' to cancel the operation.\n"
                        "```\n"
                    ).format(options)

                    msg = await bot.send_message(ctx.message.channel, message)
                    response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
                    await bot.delete_message(msg)

                    if response is None:
                        msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
                        await sleep(timeout_time)
                        await bot.delete_message(msg)
                    elif response.content == "cancel":
                        await bot.delete_message(response)
                    else:
                        await bot.delete_message(response)
                        try:
                            edit_option = int(response.content)

                            if edit_option == 1:
                                await self.edit_title(ctx, anime_to_edit_index)
                            elif edit_option == 2:
                                await self.edit_status(ctx, anime_to_edit_index)
                            elif edit_option == 3:
                                await self.edit_current_episode(ctx, anime_to_edit_index)
                            elif edit_option == 4:
                                await self.edit_last_episode(ctx, anime_to_edit_index)
                            elif edit_option == 5:
                                await self.edit_score(ctx, anime_to_edit_index)
                            elif edit_option == 6:
                                await self.edit_tags(ctx, anime_to_edit_index)
                            else:
                                raise ValueError("Option does not exist")
                        except ValueError:
                            await bot.delete_message(response)
                            msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                            await sleep(timeout_time)
                            await bot.delete_message(msg)

                except ValueError:
                    await bot.delete_message(response)
                    msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                    await sleep(timeout_time)
                    await bot.delete_message(msg)

        return

    async def remove(self, ctx):
        '''Removes an anime from the list'''

        message = (
            "```js\n"
            "Please type the name of the anime to remove.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)

            entries = ""
            tags = response.content.split(' ')
            entry_index = 0
            matching_anime = []
            for key, value in self.anime_list.items():
                entry_index += 1
                for tag in tags:
                    if self.anime_list[key].title.lower().find(tag.lower()) is not -1:
                        entries += "[{}] {}\n".format(entry_index, self.anime_list[key].title)
                        matching_anime.append(key)

            if entries == "":
                message = ":o: | Could not find any anime with that title | :o:"
                msg = await bot.send_message(ctx.message.channel, message)
                await sleep(timeout_time)
                await bot.delete_message(msg)
                return

            message = (
                "```js\n"
                "Please choose one of these entries\n"
                "\n"
                "{}"
                "\n"
                "Type 'cancel' to cancel the operation.\n"
                "```"
            ).format(entries)

            msg = await bot.send_message(ctx.message.channel, message)
            response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
            await bot.delete_message(msg)

            if response is None:
                msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
            elif response.content == "cancel":
                await bot.delete_message(response)
            else:
                await bot.delete_message(response)
                try:
                    option = int(response.content)
                    if option > entry_index:
                        raise ValueError("Option does not exist")
                    anime_to_delete_index = matching_anime[option - 1]
                    await bot.delete_message(self.anime_list[anime_to_delete_index].message)
                    del self.anime_list[anime_to_delete_index]
                    msg = await bot.send_message(
                        ctx.message.channel,
                        ":ok_hand:  | Succesfully removed anime from list | :ok_hand:"
                    )
                    await sleep(timeout_time)
                    await bot.delete_message(msg)
                except ValueError:
                    await bot.delete_message(response)
                    msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                    await sleep(timeout_time)
                    await bot.delete_message(msg)
        return

    async def modify_embed(self, anime):
        '''Modifies an anime embed'''

        embed = discord.Embed(title=anime.title, url=anime.url, color=0xff80ff)
        embed.set_thumbnail(url=anime.thumbnail)

        embed.add_field(name="Status", value=anime.status.status_name, inline=False)
        embed.add_field(name="Episodes", value=str(anime.current_episode) + '/' + str(anime.last_episode), inline=False)
        embed.add_field(name="Score", value=anime.score, inline=False)

        return embed
    
    asynce def verify_response(self, ctx, message):
        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
            return
        elif response.content == "cancel":
            await bot.delete_message(response)
            return
        else:
            await bot.delete_message(response)
            return response.content
    
    async def edit_title(self, ctx, anime_id):
        '''Edits the title of an anime on the list'''

        message = (
            "```js\n"
            "Please type the new title.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            try:
                title = str(response.content)
                anime = self.anime_list[anime_id]

                anime.set_title(title)
                embed = await self.modify_embed(anime)
                await bot.edit_message(anime.message, ' ', embed=embed)
                msg = await bot.send_message(
                    ctx.message.channel,
                    ":clap: | Title changed to {} | :clap:".format(title)
                )
                await sleep(timeout_time)
                await bot.delete_message(msg)
            except ValueError:
                await bot.delete_message(response)
                msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
        return

    async def edit_status(self, ctx, anime_id):
        '''Edits the status of an anime on the list'''

        options = (
            "[1] Watching\n"
            "[2] Dropped\n"
            "[3] Plan To Watch\n"
            "[4] Finished\n"
            "[5] Hentai\n"
        )
        message = (
            "```js\n"
            "Please select the status.\n"
            "\n"
            "{}"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        ).format(options)

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            try:
                status_index = int(response.content)
                if status_index > 5 or status_index < 1:
                    raise ValueError("Option does not exist")

                anime = self.anime_list[anime_id]

                status_name = {
                    1: "Watching",
                    2: "Dropped",
                    3: "Plan To Watch",
                    4: "Finished",
                    5: "Hentai"
                }

                anime.set_status(self.status_list[status_name[status_index]])
                embed = await self.modify_embed(anime)
                channel = bot.get_channel(str(anime.status.channel_id))

                await bot.delete_message(anime.message)
                current_message = await bot.send_message(channel, ' ', embed=embed)
                anime.set_message(current_message)
                msg = await bot.send_message(
                    ctx.message.channel,
                    ":clap: | Status changed to {} | :clap:".format(self.status_list[status_name[status_index]])
                )
                await sleep(timeout_time)
                await bot.delete_message(msg)
            except ValueError:
                await bot.delete_message(response)
                msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
        return

    async def edit_current_episode(self, ctx, anime_id):
        '''Edits the current episode of an anime on the list'''

        message = (
            "```js\n"
            "Please type the current episode you are on.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            try:
                current_episode = int(response.content)
                anime = self.anime_list[anime_id]

                if anime.last_episode is not 0:
                    if current_episode > anime.last_episode:
                        current_episode = anime.last_episode
                    elif current_episode < 0:
                        current_episode = 0

                anime.set_current_episode(current_episode)
                embed = await self.modify_embed(anime)
                await bot.edit_message(anime.message, ' ', embed=embed)
                msg = await bot.send_message(
                    ctx.message.channel,
                    ":clap: | Current episode changed to {} | :clap:".format(current_episode)
                )
                await sleep(timeout_time)
                await bot.delete_message(msg)
            except ValueError:
                await bot.delete_message(response)
                msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
        return

    async def edit_last_episode(self, ctx, anime_id):
        '''Edits the last episode of an anime on the list'''

        message = (
            "```js\n"
            "Please type the last episode of the anime.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            try:
                last_episode = int(response.content)
                anime = self.anime_list[anime_id]

                if last_episode < 0:
                    last_episode = 0

                anime.set_last_episode(last_episode)
                embed = await self.modify_embed(anime)
                await bot.edit_message(anime.message, ' ', embed=embed)
                msg = await bot.send_message(
                    ctx.message.channel,
                    ":clap: | Last episode changed to {} | :clap:".format(last_episode)
                )
                await sleep(timeout_time)
                await bot.delete_message(msg)
            except ValueError:
                await bot.delete_message(response)
                msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
        return

    async def edit_score(self, ctx, anime_id):
        '''Edits the score of an anime on the list'''

        message = (
            "```js\n"
            "Please type the score.\n"
            "\n"
            "Type 'cancel' to cancel the operation.\n"
            "```"
        )

        msg = await bot.send_message(ctx.message.channel, message)
        response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
        await bot.delete_message(msg)

        if response is None:
            msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(timeout_time)
            await bot.delete_message(msg)
        elif response.content == "cancel":
            await bot.delete_message(response)
        else:
            await bot.delete_message(response)
            try:
                score = float(response.content)
                if score > 10.0:
                    score = 10.0
                elif score < 0.0:
                    score = 0.0

                anime = self.anime_list[anime_id]
                anime.set_score(score)
                embed = await self.modify_embed(anime)
                await bot.edit_message(anime.message, ' ', embed=embed)
                msg = await bot.send_message(ctx.message.channel, ":clap: | Score changed to {} | :clap:".format(score))
                await sleep(timeout_time)
                await bot.delete_message(msg)
            except ValueError:
                await bot.delete_message(response)
                msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(timeout_time)
                await bot.delete_message(msg)
        return

    async def edit_tags(self, ctx, anime_id):
        pass


class MangaManager:
    def __init__(self, status_list):
        self.status_list = status_list

    async def add(self, ctx):
        pass

    async def edit(self, ctx):
        pass

    async def remove(self, ctx):
        pass


'''DELETE LATER'''
with open('auth.json') as f:
    auth = json.load(f)

TOKEN = auth["auth"]["token"]

bot = commands.Bot(command_prefix='%')

weeb_client = Manager(AnimeManager(anime_status_list), MangaManager(manga_status_list))


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="%help"))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(pass_context=True)
async def weeb(ctx):
    '''Weeb menu'''
    await sleep(1.0)
    await bot.delete_message(ctx.message)

    options = "[1] Anime\n[2] Manga\n"
    message = (
        "```js\n"
        "Please select one of the options.\n"
        "\n"
        "{}"
        "\n"
        "Type the number for the option you would like to select.\n"
        "Type 'cancel' to cancel the operation.\n"
        "```\n"
    ).format(options)

    msg = await bot.send_message(ctx.message.channel, message)
    response = await bot.wait_for_message(timeout=timeout_time, author=ctx.message.author)
    await bot.delete_message(msg)

    if response is None:
        msg = await bot.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
        await sleep(timeout_time)
        await bot.delete_message(msg)
    elif response.content == "1":
        await bot.delete_message(response)
        await weeb_client.anime(ctx)
    elif response.content == "2":
        await bot.delete_message(response)
        await weeb_client.manga(ctx)
    elif response.content == "cancel":
        await bot.delete_message(response)
    else:
        await bot.delete_message(response)
        msg = await bot.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
        await sleep(timeout_time)
        await bot.delete_message(msg)
    return

bot.run(TOKEN)
'''DELETE LATER'''
