import discord
import pickle
import datetime
import requests
from asyncio import sleep
from shutil import copyfile
import json


CHANNEL_ID = None
TIMEOUT_TIME = 15.0
BOT = None



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
        
    def set_title(self, title):
        self.title = title

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

    def set_title(self, title):
        self.title = title

    def set_status(self, status):
        self.status = status

    def set_current_chapter(self, current_chapter):
        self.current_chapter = current_chapter

    def set_last_chapter(self, last_chapter):
        self.last_chapter = last_chapter

    def set_score(self, score):
        self.score = score


class Manager:
    def __init__(self, anime_manager, manga_manager):
        self.anime_manager = anime_manager
        self.manga_manager = manga_manager
        self.load()

    def load(self):
        anime_list = {}
        manga_list = {}

        anime_list_save_file = "saves\\anime_list.p"
        manga_list_save_file = "saves\\manga_list.p"
        
        try:
            with open(anime_list_save_file, 'rb') as anime_pickle:
                anime_list = pickle.load(anime_pickle)
                self.anime_manager.set_list(anime_list)
                print("Anime List Loaded!")
            with open(manga_list_save_file, 'rb') as manga_pickle:
                manga_list = pickle.load(manga_pickle)
                self.manga_manager.set_list(manga_list)
                print("Manga List Loaded!")
        except FileNotFoundError:
            print("Creating new pickle files...")
            with open(anime_list_save_file, 'wb') as anime_pickle:
                pickle.dump(anime_list, anime_pickle, protocol=pickle.HIGHEST_PROTOCOL)
                self.anime_manager.set_list(anime_list)
                print("Anime List Created!")
            with open(manga_list_save_file, 'wb') as manga_pickle:
                pickle.dump(manga_list, manga_pickle, protocol=pickle.HIGHEST_PROTOCOL)
                self.manga_manager.set_list(manga_list)
                print("Anime List Created!")
        try:        
            with open("saves\\manga_messages.p", 'rb') as pkl:
                manga_current_messages = pickle.load(pkl)
                self.manga_manager.set_current_messages(manga_current_messages)
            with open("saves\\anime_messages.p", 'rb') as pkl:
                anime_current_messages = pickle.load(pkl)
                self.anime_manager.set_current_messages(anime_current_messages)    
        except FileNotFoundError:
            return

    async def dump_to_json(self):
        weeb_json = {
            "anime":
                [

                ],
            "manga":
            [

            ]
        }
        i = 0
        for key, value in self.anime_manager.anime_list.items():
            weeb_json["anime"].append({"id": value.id})
            weeb_json["anime"][i]["title"] = value.title
            weeb_json["anime"][i]["synonyms"] = value.synonyms
            weeb_json["anime"][i]["status"] = str(value.status)
            weeb_json["anime"][i]["current_episode"] = value.current_episode
            weeb_json["anime"][i]["last_episode"] = value.last_episode
            weeb_json["anime"][i]["score"] = value.score
            weeb_json["anime"][i]["url"] = value.url
            weeb_json["anime"][i]["thumbnail"] = value.thumbnail
            i += 1

        i = 0
        for key, value in self.manga_manager.manga_list.items():
            weeb_json["manga"].append({"id": value.id})
            weeb_json["manga"][i]["title"] = value.title
            weeb_json["manga"][i]["synonyms"] = value.synonyms
            weeb_json["manga"][i]["status"] = str(value.status)
            weeb_json["manga"][i]["current_chapter"] = value.current_chapter
            weeb_json["manga"][i]["last_chapter"] = value.last_chapter
            weeb_json["manga"][i]["score"] = value.score
            weeb_json["manga"][i]["url"] = value.url
            weeb_json["manga"][i]["thumbnail"] = value.thumbnail
            i += 1

        with open("saves/weeb_json.json", 'w', encoding='utf-8') as out:
            out.write(json.dumps(weeb_json, ensure_ascii=False, indent=4))

    async def init(self, bot, channel_id):
        global BOT, CHANNEL_ID
        BOT = bot
        CHANNEL_ID = channel_id
        return
                
    async def menu(self, ctx):
        '''Weeb menu'''

        await sleep(0.5)
        await BOT.delete_message(ctx.message)

        if BOT.get_channel(CHANNEL_ID) is None:
            await self.setup(ctx)
        
        options = "[1] Anime\n[2] Manga\n"
        message = (
            "```js\n"
            "Please select one of the options.\n"
            "\n"
            "{}"
            "\n"
            "Type the number for the option you would like to select.\n"
            "Type '$cancel' to cancel the operation.\n"
            "```\n"
        ).format(options)

        msg = await BOT.send_message(ctx.message.channel, message)
        response = await BOT.wait_for_message(timeout=TIMEOUT_TIME, author=ctx.message.author)
        await BOT.delete_message(msg)

        if response is None:
            msg = await BOT.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        elif response.content == "1":
            await BOT.delete_message(response)
            await self.anime(ctx)
        elif response.content == "2":
            await BOT.delete_message(response)
            await self.manga(ctx)
        elif response.content == "$cancel":
            await BOT.delete_message(response)
        else:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
    
    async def setup(self, ctx):
        message = (
            "```js\n"
            "Please type the ID of the channel to use as the list channel.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )
        
        msg = await BOT.send_message(ctx.message.channel, message)
        response = await BOT.wait_for_message(timeout=TIMEOUT_TIME, author=ctx.message.author)
        await BOT.delete_message(msg)
        
        if response is None:
            return
        elif response.content == "$cancel":
            await BOT.delete_message(response)
        elif BOT.get_channel(response.content) is None:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Channel does not exist | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return
            
        CHANNEL_ID = response.content
        
        with open('auth.json', 'rb') as f:
            auth = json.load(f)
        auth["channel"]["channel_id"] = CHANNEL_ID
        with open('auth.json', 'w') as f:
            json.dump(auth, f)
        
        await BOT.delete_message(response)
        msg = await BOT.send_message(ctx.message.channel, ":ok: | Channel successfully setup | :ok:")
        await sleep(2.0)
        await BOT.delete_message(msg)
        return
    
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
            "Type '$cancel' to cancel the operation.\n"
            "```\n"
        ).format(options)

        response = await self.anime_manager.get_response(ctx, message)
        if response is None:
            return

        try:
            option = int(response.content)

            if option == 1:
                await self.anime_manager.add(ctx)
            elif option == 2:
                await self.anime_manager.edit(ctx)
            elif option == 3:
                await self.anime_manager.remove(ctx)
            else:
                raise ValueError("Option does not exist.")

        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)

        self.anime_manager.save()
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
            "Type '$cancel' to cancel the operation.\n"
            "```\n"
        ).format(options)

        response = await self.manga_manager.get_response(ctx, message)
        if response is None:
            return

        try:
            option = int(response.content)

            if option == 1:
                await self.manga_manager.add(ctx)
            elif option == 2:
                await self.manga_manager.edit(ctx)
            elif option == 3:
                await self.manga_manager.remove(ctx)
            else:
                raise ValueError("Option does not exist.")

        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)

        self.manga_manager.save()
        return


class AnimeManager:
    def __init__(self):
        self.current_messages = []
        self.anime_list = {}
    
    @staticmethod
    def modify_embed(anime):
        '''Modifies an anime embed'''

        embed = discord.Embed(title=anime.title, url=anime.url, color=0xff80ff)
        embed.set_thumbnail(url=anime.thumbnail)

        embed.add_field(name="Status", value=anime.status, inline=False)
        embed.add_field(name="Episodes", value=str(anime.current_episode) + '/' + str(anime.last_episode), inline=False)
        embed.add_field(name="Score", value=anime.score, inline=False)

        return embed
    
    @staticmethod
    def get_thumbnail(anime_id):
        query = '''
        query ($id: Int) {
            Media (id: $id, type: ANIME) {
                id
                coverImage {
                    large
                }
            }
        }
        '''
        variables = {
            'id': anime_id
        }
        url = 'https://graphql.anilist.co'
        anilist_response = requests.post(url, json={'query': query, 'variables': variables})
        data = anilist_response.json()
        data = data["data"]["Media"]
        return data["coverImage"]["large"]
    
    async def update_list(self):
        '''Updates the anime list'''
        channel = BOT.get_channel(CHANNEL_ID)
        
        sorted_list = ["Watching", "Dropped", "Plan To Watch", "Finished"]
        
        if len(self.current_messages) > 2:
            await BOT.delete_messages(self.current_messages)
        self.current_messages = []
        
        section_msg = await BOT.send_file(channel, "static/ANIME_LIST_BANNER.jpg", filename="ANIME_LIST_BANNER.jpg", content=' ')
        await BOT.pin_message(section_msg)
        self.current_messages.append(section_msg)
        
        for status in sorted_list:
            status_msg = await BOT.send_message(channel, status) # Replace message with status image banner or more better looking message
            self.current_messages.append(status_msg)
            for entry in self.anime_list.values():
                if str(entry.status) == status:
                    entry.status = status # Delete
                    entry.thumbnail = self.get_thumbnail(entry.id) #Delete
                    embed = self.modify_embed(entry)
                    entry_message = await BOT.send_message(channel, ' ', embed=embed)
                    self.current_messages.append(entry_message)
                    await sleep(0.5)
        self.save()
        return
    
    def set_current_messages(self, current_messages):
        self.current_messages = current_messages
    
    def set_list(self, anime_list):
        self.anime_list = anime_list

    def save(self):
        anime_list_save_file = "saves\\anime_list.p"
        
        backup_file = "saves\\backup\\{}".format(
            datetime.datetime.now().strftime("anime_list_backup_%H_%M_%d_%m_%Y.bck")
        )

        copyfile(anime_list_save_file, backup_file)

        with open(anime_list_save_file, 'wb') as list_pickle:
            pickle.dump(self.anime_list, list_pickle, protocol=pickle.HIGHEST_PROTOCOL)
        with open("saves\\anime_messages.p", 'wb') as pkl:
            pickle.dump(self.current_messages, pkl, protocol=pickle.HIGHEST_PROTOCOL)
        return

    async def add(self, ctx):
        '''Adds an anime to the list'''

        message = (
            "```js\n"
            "Please type the name of the anime to add.\n"
            "\n"
            "Or type '$id <id of anime>'.\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

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
            'perPage': 10
        }
        url = 'https://graphql.anilist.co'

        if response.content.startswith("$id "):
            try:
                anime_id = int(response.content.replace('$id ', ''))
                variables["id"] = anime_id
                del variables["search"]
            except ValueError:
                message = ":o: | Could not find any anime with that id | :o:"
                msg = await BOT.send_message(ctx.message.channel, message)
                await sleep(TIMEOUT_TIME)
                await BOT.delete_message(msg)
                return

        anilist_response = requests.post(url, json={'query': query, 'variables': variables})
        data = anilist_response.json()
        data = data["data"]["Page"]

        entries = ""
        for i, anime_entry in enumerate(data["media"]):
            entries += "[{}] {}\n".format(i + 1, anime_entry["title"]["romaji"])

        if entries == "":
            message = ":o: | Could not find any anime with that title | :o:"
            msg = await BOT.send_message(ctx.message.channel, message)
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return

        message = (
            "```\n"
            "Please select the anime you would like to add to the list.\n"
            "\n"
            "{}"
            "\n"
            "Type the number for the option you would like to select.\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(entries)

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            anime_entry_index = int(response.content) - 1
            if anime_entry_index + 1 > data["pageInfo"]["total"]:
                raise ValueError('Value Too High')

            new_anime_json = data["media"][anime_entry_index]

            synonyms = new_anime_json["synonyms"]
            synonyms.append(new_anime_json["title"]["english"])
            synonyms.append(new_anime_json["title"]["romaji"])
            synonyms = [x for x in synonyms if x is not None]

            new_anime = Anime(
                new_anime_json["id"],
                new_anime_json["title"]["romaji"],
                synonyms,
                "Plan To Watch",
                new_anime_json["episodes"],
                new_anime_json["siteUrl"],
                new_anime_json["coverImage"]["large"]
            )
            self.anime_list[new_anime_json["id"]] = new_anime
            
            await self.update_list()
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit(self, ctx):
        '''Edits an anime on the list'''

        message = (
            "```js\n"
            "Please type the name of the anime to edit.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        entries = ""
        tags = response.content.split(' ')
        entry_index = 0
        matching_anime = []
        for key, value in self.anime_list.items():
            for tag in tags:
                if self.anime_list[key].title.lower().find(tag.lower()) is not -1:
                    if key not in matching_anime:
                        entry_index += 1
                        entries += "[{}] {}\n".format(entry_index, self.anime_list[key].title)
                        matching_anime.append(key)

        if entries == "":
            message = ":o: | Could not find any anime with that title | :o:"
            msg = await BOT.send_message(ctx.message.channel, message)
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return

        message = (
            "```\n"
            "Please choose one of these entries\n"
            "\n"
            "{}"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(entries)

        response = await self.get_response(ctx, message)
        if response is None:
            return

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
                "Type '$cancel' to cancel the operation.\n"
                "```\n"
            ).format(options)

            response = await self.get_response(ctx, message)
            if response is None:
                return

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
                await BOT.delete_message(response)
                msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(TIMEOUT_TIME)
                await BOT.delete_message(msg)

        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)

        return

    async def remove(self, ctx):
        '''Removes an anime from the list'''

        message = (
            "```js\n"
            "Please type the name of the anime to remove.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        entries = ""
        tags = response.content.split(' ')
        entry_index = 0
        matching_anime = []
        for key, value in self.anime_list.items():
            for tag in tags:
                if self.anime_list[key].title.lower().find(tag.lower()) is not -1:
                    if key not in matching_anime:
                        entry_index += 1
                        entries += "[{}] {}\n".format(entry_index, self.anime_list[key].title)
                        matching_anime.append(key)

        if entries == "":
            message = ":o: | Could not find any anime with that title | :o:"
            msg = await BOT.send_message(ctx.message.channel, message)
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return

        message = (
            "```\n"
            "Please choose one of these entries\n"
            "\n"
            "{}"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(entries)

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            option = int(response.content)
            if option > entry_index:
                raise ValueError("Option does not exist")
            anime_to_delete_index = matching_anime[option - 1]
            del self.anime_list[anime_to_delete_index]
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":ok_hand:  | Succesfully removed anime from list | :ok_hand:"
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    @staticmethod
    async def get_response(ctx, message):
        msg = await BOT.send_message(ctx.message.channel, message)
        response = await BOT.wait_for_message(timeout=TIMEOUT_TIME, author=ctx.message.author)
        await BOT.delete_message(msg)

        if response is None:
            msg = await BOT.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return
        elif response.content == "$cancel":
            await BOT.delete_message(response)
            return
        else:
            await BOT.delete_message(response)
            return response
    
    async def edit_title(self, ctx, anime_id):
        '''Edits the title of an anime on the list'''

        message = (
            "```js\n"
            "Please type the new title.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            title = str(response.content)
            anime = self.anime_list[anime_id]

            anime.set_title(title)
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Title changed to {} | :clap:".format(title)
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
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
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(options)

        response = await self.get_response(ctx, message)
        if response is None:
            return

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

            if status_name[status_index] == "Finished":
                anime.set_current_episode(anime.last_episode)

            anime.set_status(status_name[status_index])
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Status changed to {} | :clap:".format(status_name[status_index])
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_current_episode(self, ctx, anime_id):
        '''Edits the current episode of an anime on the list'''

        message = (
            "```js\n"
            "Please type the current episode you are on.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            current_episode = int(response.content)
            anime = self.anime_list[anime_id]

            if anime.last_episode is not 0:
                if current_episode > anime.last_episode:
                    current_episode = anime.last_episode
                elif current_episode < 0:
                    current_episode = 0

            anime.set_current_episode(current_episode)
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Current episode changed to {} | :clap:".format(current_episode)
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_last_episode(self, ctx, anime_id):
        '''Edits the last episode of an anime on the list'''

        message = (
            "```js\n"
            "Please type the last episode of the anime.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            last_episode = int(response.content)
            anime = self.anime_list[anime_id]

            if last_episode < 0:
                last_episode = 0

            anime.set_last_episode(last_episode)
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Last episode changed to {} | :clap:".format(last_episode)
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_score(self, ctx, anime_id):
        '''Edits the score of an anime on the list'''

        message = (
            "```js\n"
            "Please type the score.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            score = float(response.content)
            if score > 10.0:
                score = 10.0
            elif score < 0.0:
                score = 0.0

            anime = self.anime_list[anime_id]
            anime.set_score(score)
            await self.update_list()
            msg = await BOT.send_message(ctx.message.channel, ":clap: | Score changed to {} | :clap:".format(score))
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_tags(self, ctx, anime_id):
        '''Add or remove a tag of an anime on the list'''
        pass


class MangaManager:
    def __init__(self):
        self.current_messages = []
        self.manga_list = {}
    
    @staticmethod
    def modify_embed(manga):
        '''Modifies a manga embed'''

        embed = discord.Embed(title=manga.title, url=manga.url, color=0xff80ff)
        embed.set_thumbnail(url=manga.thumbnail)

        embed.add_field(name="Status", value=manga.status, inline=False)
        embed.add_field(name="Chapters", value=str(manga.current_chapter) + '/' + str(manga.last_chapter), inline=False)
        embed.add_field(name="Score", value=manga.score, inline=False)

        return embed
    
    @staticmethod
    def get_thumbnail(manga_id):
        query = '''
        query ($id: Int) {
            Media (id: $id, type: MANGA) {
                id
                coverImage {
                    large
                }
            }
        }
        '''
        variables = {
            'id': manga_id
        }
        url = 'https://graphql.anilist.co'
        anilist_response = requests.post(url, json={'query': query, 'variables': variables})
        data = anilist_response.json()
        data = data["data"]["Media"]
        return data["coverImage"]["large"]
    
    
    async def update_list(self):
        '''Updates the manga list'''
        channel = BOT.get_channel(CHANNEL_ID)
        
        sorted_list = ["Reading", "Dropped", "Plan To Read", "Finished"]
        
        if len(self.current_messages) > 2:
            await BOT.delete_messages(self.current_messages)
        self.current_messages = []
        
        section_msg = await BOT.send_file(channel, "static/MANGA_LIST_BANNER.jpg", filename="MANGA_LIST_BANNER.jpg", content=' ')
        await BOT.pin_message(section_msg)
        self.current_messages.append(section_msg)
        
        for status in sorted_list:
            status_msg = await BOT.send_message(channel, status) # Replace message with status image banner or more better looking message
            self.current_messages.append(status_msg)
            for entry in self.manga_list.values():
                if str(entry.status) == status:
                    entry.status = status # Delete
                    entry.thumbnail = self.get_thumbnail(entry.id) #Delete
                    embed = self.modify_embed(entry)
                    entry_message = await BOT.send_message(channel, ' ', embed=embed)
                    self.current_messages.append(entry_message)
                    await sleep(0.5)
        self.save()
        return
    
    def set_current_messages(self, current_messages):
        self.current_messages = current_messages
    
    def set_list(self, manga_list):
        self.manga_list = manga_list

    def save(self):
        manga_list_save_file = "saves\\manga_list.p"
        
        backup_file = "saves\\backup\\{}".format(
            datetime.datetime.now().strftime("manga_list_backup_%H_%M_%d_%m_%Y.bck")
        )

        copyfile(manga_list_save_file, backup_file)

        with open(manga_list_save_file, 'wb') as list_pickle:
            pickle.dump(self.manga_list, list_pickle, protocol=pickle.HIGHEST_PROTOCOL)
        with open("saves\\manga_messages.p", 'wb') as pkl:
            pickle.dump(self.current_messages, pkl, protocol=pickle.HIGHEST_PROTOCOL)
        return

    async def add(self, ctx):
        '''Adds a manga to the list'''

        message = (
            "```js\n"
            "Please type the name of the manga to add.\n"
            "\n"
            "Or type '$id <id of anime>'.\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        query = '''
        query ($id: Int, $page: Int, $perPage: Int, $search: String) {
            Page (page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    perPage
                }
                media (id: $id, type: MANGA, search: $search) {
                    id
                    type
                    title {
                        romaji
                        english
                    }
                    chapters
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
            'perPage': 10
        }
        url = 'https://graphql.anilist.co'

        if response.content.startswith("$id "):
            try:
                manga_id = int(response.content.replace('$id ', ''))
                variables["id"] = manga_id
                del variables["search"]
            except ValueError:
                message = ":o: | Could not find any manga with that id | :o:"
                msg = await BOT.send_message(ctx.message.channel, message)
                await sleep(TIMEOUT_TIME)
                await BOT.delete_message(msg)
                return

        anilist_response = requests.post(url, json={'query': query, 'variables': variables})
        data = anilist_response.json()
        data = data["data"]["Page"]

        entries = ""
        for i, manga_entry in enumerate(data["media"]):
            entries += "[{}] {}\n".format(i + 1, manga_entry["title"]["romaji"])

        if entries == "":
            message = ":o: | Could not find any manga with that title | :o:"
            msg = await BOT.send_message(ctx.message.channel, message)
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return

        message = (
            "```\n"
            "Please select the manga you would like to add to the list.\n"
            "\n"
            "{}"
            "\n"
            "Type the number for the option you would like to select.\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(entries)

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            manga_entry_index = int(response.content) - 1
            if manga_entry_index + 1 > data["pageInfo"]["total"]:
                raise ValueError('Value Too High')

            new_manga_json = data["media"][manga_entry_index]

            synonyms = new_manga_json["synonyms"]
            synonyms.append(new_manga_json["title"]["english"])
            synonyms.append(new_manga_json["title"]["romaji"])
            synonyms = [x for x in synonyms if x is not None]

            chapters = new_manga_json["chapters"]
            if chapters is None:
                chapters = 0

            new_manga = Manga(
                new_manga_json["id"],
                new_manga_json["title"]["romaji"],
                synonyms,
                "Plan To Read",
                chapters,
                new_manga_json["siteUrl"],
                new_manga_json["coverImage"]["large"]
            )
            self.manga_list[new_manga_json["id"]] = new_manga

            await self.update_list()
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit(self, ctx):
        '''Edits a manga on the list'''

        message = (
            "```js\n"
            "Please type the name of the manga to edit.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        entries = ""
        tags = response.content.split(' ')
        entry_index = 0
        matching_manga = []
        for key, value in self.manga_list.items():
            for tag in tags:
                if self.manga_list[key].title.lower().find(tag.lower()) is not -1:
                    if key not in matching_manga:
                        entry_index += 1
                        entries += "[{}] {}\n".format(entry_index, self.manga_list[key].title)
                        matching_manga.append(key)

        if entries == "":
            message = ":o: | Could not find any manga with that title | :o:"
            msg = await BOT.send_message(ctx.message.channel, message)
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return

        message = (
            "```\n"
            "Please choose one of these entries\n"
            "\n"
            "{}"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(entries)

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            option = int(response.content)
            if option > entry_index:
                raise ValueError("Option does not exist")
            manga_to_edit_index = matching_manga[option - 1]

            options = (
                "[1] Title\n"
                "[2] Status\n"
                "[3] Current chapter\n"
                "[4] Last chapter\n"
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
                "Type '$cancel' to cancel the operation.\n"
                "```\n"
            ).format(options)

            response = await self.get_response(ctx, message)
            if response is None:
                return

            try:
                edit_option = int(response.content)

                if edit_option == 1:
                    await self.edit_title(ctx, manga_to_edit_index)
                elif edit_option == 2:
                    await self.edit_status(ctx, manga_to_edit_index)
                elif edit_option == 3:
                    await self.edit_current_chapter(ctx, manga_to_edit_index)
                elif edit_option == 4:
                    await self.edit_last_chapter(ctx, manga_to_edit_index)
                elif edit_option == 5:
                    await self.edit_score(ctx, manga_to_edit_index)
                elif edit_option == 6:
                    await self.edit_tags(ctx, manga_to_edit_index)
                else:
                    raise ValueError("Option does not exist")
            except ValueError:
                await BOT.delete_message(response)
                msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
                await sleep(TIMEOUT_TIME)
                await BOT.delete_message(msg)

        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)

        return

    async def remove(self, ctx):
        '''Removes a manga from the list'''

        message = (
            "```js\n"
            "Please type the name of the manga to remove.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        entries = ""
        tags = response.content.split(' ')
        entry_index = 0
        matching_manga = []
        for key, value in self.manga_list.items():
            for tag in tags:
                if self.manga_list[key].title.lower().find(tag.lower()) is not -1:
                    if key not in matching_manga:
                        entry_index += 1
                        entries += "[{}] {}\n".format(entry_index, self.manga_list[key].title)
                        matching_manga.append(key)

        if entries == "":
            message = ":o: | Could not find any manga with that title | :o:"
            msg = await BOT.send_message(ctx.message.channel, message)
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return

        message = (
            "```\n"
            "Please choose one of these entries\n"
            "\n"
            "{}"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(entries)

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            option = int(response.content)
            if option > entry_index:
                raise ValueError("Option does not exist")
            manga_to_delete_index = matching_manga[option - 1]
            del self.manga_list[manga_to_delete_index]
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":ok_hand:  | Succesfully removed manga from list | :ok_hand:"
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    @staticmethod
    async def get_response(ctx, message):
        msg = await BOT.send_message(ctx.message.channel, message)
        response = await BOT.wait_for_message(timeout=TIMEOUT_TIME, author=ctx.message.author)
        await BOT.delete_message(msg)

        if response is None:
            msg = await BOT.send_message(ctx.message.channel, ":alarm_clock: | Timeout | :alarm_clock:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
            return None
        elif response.content == "$cancel":
            await BOT.delete_message(response)
            return None
        else:
            await BOT.delete_message(response)
            return response

    async def edit_title(self, ctx, manga_id):
        '''Edits the title of a manga on the list'''

        message = (
            "```js\n"
            "Please type the new title.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            title = str(response.content)
            manga = self.manga_list[manga_id]

            manga.set_title(title)
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Title changed to {} | :clap:".format(title)
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_status(self, ctx, manga_id):
        '''Edits the status of a manga on the list'''

        options = (
            "[1] Reading\n"
            "[2] Dropped\n"
            "[3] Plan To Read\n"
            "[4] Finished\n"
        )
        message = (
            "```js\n"
            "Please select the status.\n"
            "\n"
            "{}"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        ).format(options)

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            status_index = int(response.content)
            if status_index > 5 or status_index < 1:
                raise ValueError("Option does not exist")

            manga = self.manga_list[manga_id]

            status_name = {
                1: "Reading",
                2: "Dropped",
                3: "Plan To Read",
                4: "Finished"
            }

            if status_name[status_index] == "Finished":
                manga.set_current_chapter(manga.last_chapter)

            manga.set_status(status_name[status_index])
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Status changed to {} | :clap:".format(status_name[status_index])
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_current_chapter(self, ctx, manga_id):
        '''Edits the current chapter of a manga on the list'''

        message = (
            "```js\n"
            "Please type the current chapter you are on.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            current_chapter = int(response.content)
            manga = self.manga_list[manga_id]

            if manga.last_chapter is not 0:
                if current_chapter > manga.last_chapter:
                    current_chapter = manga.last_chapter
                elif current_chapter < 0:
                    current_chapter = 0

            manga.set_current_chapter(current_chapter)
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Current chapter changed to {} | :clap:".format(current_chapter)
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_last_chapter(self, ctx, manga_id):
        '''Edits the last chapter of a manga on the list'''

        message = (
            "```js\n"
            "Please type the last chapter of the manga.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            last_chapter = int(response.content)
            manga = self.manga_list[manga_id]

            if last_chapter < 0:
                last_chapter = 0

            manga.set_last_chapter(last_chapter)
            await self.update_list()
            msg = await BOT.send_message(
                ctx.message.channel,
                ":clap: | Last chapter changed to {} | :clap:".format(last_chapter)
            )
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_score(self, ctx, manga_id):
        '''Edits the score of a manga on the list'''

        message = (
            "```js\n"
            "Please type the score.\n"
            "\n"
            "Type '$cancel' to cancel the operation.\n"
            "```"
        )

        response = await self.get_response(ctx, message)
        if response is None:
            return

        try:
            score = float(response.content)
            if score > 10.0:
                score = 10.0
            elif score < 0.0:
                score = 0.0

            manga = self.manga_list[manga_id]
            manga.set_score(score)
            await self.update_list()
            msg = await BOT.send_message(ctx.message.channel, ":clap: | Score changed to {} | :clap:".format(score))
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        except ValueError:
            await BOT.delete_message(response)
            msg = await BOT.send_message(ctx.message.channel, ":x: | Invalid option | :x:")
            await sleep(TIMEOUT_TIME)
            await BOT.delete_message(msg)
        return

    async def edit_tags(self, ctx, manga_id):
        '''Add or remove a tag of an anime on the list'''
        pass
