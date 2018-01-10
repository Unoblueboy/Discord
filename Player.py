import asyncio
from discord.ext.commands import Bot

class Player:
    def __init__(self, username, user, bot = None):
        self.username = username
        self.user = user
        self.president = False
        self.chancellor = False
        self.prevGovern = False
        self.fascist = False
        self.hitler = False
        self.dead = False
        self.bot = None
        if bot:
            self.bot = bot

    async def tell(self, message):
        if self.bot:
            await self.bot.send_message(self.user, message)
        else:
            print(self.username + ": " + message)

    async def request(self, role, allowed, request_text = "", retry_text = "", print_allowed = False):
        if request_text == "":
            request_text = "Please choose a suitable " + role + " (Select them by entering their user name)"
        if retry_text == "":
            retry_text = "Please choose a valid " + role
        choice = ""
        while True:
            if self.bot:
                # TODO Edit the function parameters so that you change the message to be entered
                # Instead of just editing the role being asked for
                await self.bot.send_message(self.user, request_text)
                if print_allowed:
                    await self.bot.send_message(self.user, "Your Choices are")
                    choice_string = ""
                    for c in allowed:
                        choice_string += " • "+c+"\n"
                    await self.bot.send_message(self.user, choice_string)
                msg = await self.bot.wait_for_message(author = self.user)
                choice = msg.content

            else:
                choice = input(self.username + ": " + request_text)

            if choice in [obj for obj in allowed]:
                return choice
            else:
                await self.bot.send_message(self.user, retry_text)

        return choice

    async def get_vote(self,yes,no,x):
        await self.bot.send_message(self.user, "Do you approve of this government, y/n?")
        # msg = await my_bot.wait_for_message(author=self.user)
        # try:
        #     msg = msg.content.lower()
        # except:
        #     pass
        # while msg not in ["y","n"]:
        #     my_bot.send_message(self.user, "Please enter valid data")
        #     msg = await my_bot.wait_for_message(author=self.user)
        #     try:
        #         msg = msg.content.lower()
        #     except:
        #         pass
        vote = await self.request("vote", 
        ["y","Y","n","N"],
        request_text = "Please vote if you would like to elect the currently nominated government (y/n)",
        retry_text = "Please choose a valid option"
        )
        if vote.lower() == "y":
            yes.append(self.username)
        else:
            no.append(self.username)
        del x[0]

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.__str__()
