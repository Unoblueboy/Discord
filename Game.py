import Player
import Tracks
import random
import math
import asyncio
from discord.ext.commands import Bot

class Players:
    def __init__(self, players):
        self.players = players

    def add_player(self,player):
        self.players.append(player)

    def find_player(self, username):
        for user in self.players:
            if user.username == username:
                return user

    def set_president(self,president=None):
        if president == None:
            self.players.players[0].president=True
        else:
            for player in self.players:
                if player == president:
                    player.president = True
                else:
                    player.president = False

    def find_president(self):
        for player in self.players:
            if player.president:
                return player

    def set_chancellor(self,chancellor):
        for player in self.players:
            if player == chancellor:
                player.chancellor = True
            else:
                player.chancellor = False

    def find_chancellor(self):
        for player in self.players:
            if player.chancellor:
                return player

    def find_next_player(self, player=None):
        if player == None:
            return self.players[0]
        else:
            index = self.players.index(player)
            nextind = (index + 1) % len(self)
            nextp = self.players[nextind]
            while nextp.dead:
                index = self.players.index(nextp)
                nextind = (index + 1) % len(self)
                nextp = self.players[nextind]
            return nextp

    def __len__(self):
        return len(self.players)

class Deck:
    def __init__(self, deck):
        self.deck = deck
        self.discard = []

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self,n):
        hand = self.deck[:n]
        del self.deck[:n]
        return hand

    def peak(self,n):
        hand = self.deck[:n]
        return hand

    def discardCard(self, card, hand):
        index = hand.index(card)
        self.discard.append(hand[index])
        del hand[index]

    def reshuffle(self):
        self.deck = self.deck + self.discard
        self.discard = []
        self.shuffle()

    def __len__(self):
        return len(self.deck)

class Game:
    def __init__(self,players, bot=None, channel=None):
        # Get all of the players
        self.players = Players(players)
        self.noOfPlayers = len(self.players)
        self.bot = bot
        self.channel = channel
        self.libtrack = Tracks.LiberalTrack()
        self.fastrack = Tracks.Track()
        self.deck = Deck(["L"]*6+["F"]*11)
        self.electionTracker = 0
        self.veto = False
        self.specialElection=0

    async def play(self):
        if self.noOfPlayers<2:
            raise Exception("There are not enough players")
        elif self.noOfPlayers>10:
            raise Exception("There are too many players")
        else:
            # Get the relevant track
            if self.noOfPlayers <= 6:
                self.fastrack = Tracks.FascistTrack1()
            elif self.noOfPlayers <= 8:
                self.fastrack = Tracks.FascistTrack2()
            else:
                self.fastrack = Tracks.FascistTrack3()
            await self.bot.send_message(self.channel,
                                        "The Liberal Track is " + ("").join(self.libtrack.track_string_list))
            await self.bot.send_message(self.channel,
                                        "The Fascist Track is " + ("").join(self.fastrack.track_string_list))



            # Shuffle player Order
            random.shuffle(self.players.players)
            await self.bot.send_message(self.channel,
                                        "The turn order is " + (", ").join([str(player) for player in self.players.players]))

            # Shuffle Deck
            self.deck.shuffle()

            # Choose the fascist
            for fascists in random.sample(self.players.players,math.ceil((self.noOfPlayers-4)/2)):
                fascists.fascist = True

            # Choose Hitler
            self.hitler = random.sample(self.players.players,1)[0]
            while self.hitler.fascist:
                self.hitler = random.sample(self.players.players,1)[0]
            self.hitler.hitler=True

            assurance = [""]*self.noOfPlayers
            # Tell everyone who they are
            for player in self.players.players:
                asyncio.ensure_future(self.tellRoles(player, assurance))

            while len(assurance)>0:
                await asyncio.sleep(1)
            curpres=""
            skip = False

            # While no-one has won
            while True:

                if self.specialElection == 1:
                    await self.bot.send_message(self.channel,
                    "The president is currently choosing the next president")
                    curpres = self.players.find_president()
                    self.specialElection = 2
                    # Choose nextpres
                    approved = [player.username for player in self.players.players if not (player.president or player.dead)]
                    presUser = await self.players.find_president().request("president",
                        approved,
                        print_allowed = True)
                    self.players.set_president(self.players.find_player(presUser))
                    await self.bot.send_message(self.channel, "The current president is " + str(self.players.find_president()))
                else:
                    if self.specialElection == 2:
                        await self.bot.send_message(self.channel,
                        "The turn order has returned back to normal")
                        self.players.set_president(curpres)
                        self.specialElection = 0
                    # Set the next player as president
                    self.players.set_president(self.players.find_next_player(self.players.find_president()))
                    await self.bot.send_message(self.channel, "The current president is " + str(self.players.find_president()))

                # President choose chancellor
                approved = [player.username for player in self.players.players if not (player.president or player.prevGovern or player.dead)]
                if len(approved)!=0:
                    chancellorUser = await self.players.find_president().request("chancellor",
                        approved,
                        print_allowed = True)
                    self.players.set_chancellor(self.players.find_player(chancellorUser))

                    await self.bot.send_message(self.channel,
                    "The current president is " + str(self.players.find_president()) + " and the current chancellor is " + str(self.players.find_chancellor()))

                    # Everyone vote
                    yes = []
                    no = []
                    yes, no = await self.vote()

                    if len(yes) == 0:
                        yes = ["no-one"]
                    if len(no) == 0:
                        no = ["no-one"]
                    await self.bot.send_message(self.channel,
                    str(", ".join(yes)) + " voted yes and " + str(", ".join(no)) + " voted no")
                else:
                    await self.bot.send_message(self.channel,
                    "The president can't choose anyone who isn't term limited")

                if self.specialElection == 0:
                    # If vote fails or president can't choose anyone
                    while len(yes) < len(no) or len(approved) == 0:

                        # Increment election tracker
                        self.electionTracker += 1

                        # if the election tracker becomes 3
                        if self.electionTracker == 3:
                            result = [None]

                            # play the policy at the top of the deck
                            card=self.deck.draw(1)[0]
                            if card == "L":
                                result = self.libtrack.update()
                                await self.bot.send_message(self.channel,
                                "A liberal card was played")
                            else:
                                result = self.fastrack.update()
                                await self.bot.send_message(self.channel,
                                "A fascist card was played")

                            lib_track_str = []
                            for x in range(1,6):
                                if x <= self.libtrack.policies:
                                    lib_track_str.append(Tracks.Track.liberal)
                                else:
                                    lib_track_str.append(self.libtrack.track_string_list[x-1])

                            fas_track_str = []        
                            for x in range(1,7):
                                if x <= self.fastrack.policies:
                                    fas_track_str.append(Tracks.Track.fascist)
                                else:
                                    fas_track_str.append(self.fastrack.track_string_list[x-1])
                            await self.bot.send_message(self.channel,
                            "Liberal Policies: " + ("").join(lib_track_str))
                            await self.bot.send_message(self.channel,
                            "Fascist Policies: " + ("").join(fas_track_str))

                            if Tracks.Track.veto in result:
                                self.veto = True

                            if Tracks.Track.win in result:
                                break

                            # No-one is term limited
                            for player in self.players.players:
                                player.prevGovern = False

                            # Reset the election Tracker
                            self.electionTracker=0

                            # Make sure there are always enough cards
                            if len(self.deck) <= 3:
                                self.deck.reshuffle()


                        # Set the next player as president
                        self.players.set_president(self.players.find_next_player(self.players.find_president()))
                        await self.bot.send_message(self.channel, "The current president is " + str(self.players.find_president()))

                        # President choose chancellor
                        approved = [player.username for player in self.players.players if not (player.president or player.prevGovern or player.dead)]
                        if len(approved) > 0:
                            chancellorUser = await self.players.find_president().request("Chancellor",
                                approved,
                                print_allowed = True)
                            self.players.set_chancellor(self.players.find_player(chancellorUser))

                            await self.bot.send_message(self.channel, "The current chancellor is " + str(self.players.find_chancellor()))


                            # revote
                            yes = []
                            no = []
                            yes, no = await self.vote()

                            await self.bot.send_message(self.channel,
                            str(yes) + " voted yes and " + str(no) + " voted no")
                        else:
                            await self.bot.send_message(self.channel,
                            "The president can't choose anyone who isn't term limited")

                    # reset election tracker
                    self.electionTracker = 0

                elif len(yes)<len(no):
                    electionTracker += 1
                    continue

                if self.libtrack.policies >= 5:
                    break
                if self.fastrack.policies >= 6:
                    break
                if self.hitler.dead:
                    break
                if self.fastrack.policies >= 3 and self.players.find_chancellor().hitler:
                    break


                # This is the current government
                for player in self.players.players:
                    player.prevGovern = False
                self.players.find_chancellor().prevGovern = True
                if len(self.players.players) >5:
                    self.players.find_president().prevGovern = True

                # The president gets the top three cards
                cards = self.deck.draw(3)
                await self.players.find_president().tell("Here are all of the available cards")
                for card in ["Liberal" if c == "L" else "Fascist" for c in cards]:
                    await self.players.find_president().tell(card)
                presDiscard = await self.players.find_president().request("discard",
                cards,
                request_text = "Please choose a card to discard ('F' for Fascist, 'L' for Liberal)",
                retry_text = "Please choose a valid card to discard")

                # President discards 1 card
                self.deck.discardCard(presDiscard, cards)

                await self.players.find_chancellor().tell("Here are all of the available cards")
                for card in ["Liberal" if c == "L" else "Fascist" for c in cards]:
                    await self.players.find_chancellor().tell(card)

                if self.veto:
                    chanDiscard = await self.players.find_chancellor().request("discard",
                    cards+["V"],
                    request_text = "Please choose a card to discard ('F' for Fascist, 'L' for Liberal, 'V' to veto (discard all current cards))",
                    retry_text = "Please choose a valid card to discard")
                    if chanDiscard == "V":
                        presApproval = await self.players.find_president().request("veto approval",
                        ["y","Y","n","N"],
                        request_text = "The chancellor wants to veto all his cards, do you agree (y/n)?",
                        retry_text = "Please answer the question"
                        )
                        if presApproval.lower() == "n":
                            await self.players.find_chancellor().tell("Here are all of the available cards")
                            for card in ["Liberal" if c == "L" else "Fascist" for c in cards]:
                                await self.players.find_chancellor().tell(card)
                            # Chancellor gets remaining 2 cards
                            chanDiscard = await self.players.find_chancellor().request("discard",
                            cards,
                            request_text = "Please choose a card to discard ('F' for Fascist, 'L' for Liberal)",
                            retry_text = "Please choose a valid card to discard")

                            # Chancellor discards one card, playing the other
                            self.deck.discardCard(chanDiscard, cards)
                        else:
                            self.deck.discardCard(cards[0], cards)
                            self.deck.discardCard(cards[0], cards)
                    else:
                        self.deck.discardCard(chanDiscard, cards)
                else:
                    # Chancellor gets remaining 2 cards
                    chanDiscard = await self.players.find_chancellor().request("discard",
                    cards,
                    request_text = "Please choose a card to discard ('F' for Fascist, 'L' for Liberal)",
                    retry_text = "Please choose a valid card to discard")

                    # Chancellor discards one card, playing the other
                    self.deck.discardCard(chanDiscard, cards)
                # DEBUG print(cards)

                # Make sure there are always enough cards
                if len(self.deck) <= 3:
                    self.deck.reshuffle()

                # Relevent power is unlocked and enacted
                results = [None]
                if len(cards) != 0:
                    if cards[0] == "L":
                        results = self.libtrack.update()
                        await self.bot.send_message(self.channel,
                        "A liberal card was played")
                    else:
                        results = self.fastrack.update()
                        await self.bot.send_message(self.channel,
                        "A fascist card was played")
                    lib_track_str = []
                    for x in range(1,6):
                        if x <= self.libtrack.policies:
                            lib_track_str.append(Tracks.Track.liberal)
                        else:
                            lib_track_str.append(self.libtrack.track_string_list[x-1])

                    fas_track_str = []        
                    for x in range(1,7):
                        if x <= self.fastrack.policies:
                            fas_track_str.append(Tracks.Track.fascist)
                        else:
                            fas_track_str.append(self.fastrack.track_string_list[x-1])
                    await self.bot.send_message(self.channel,
                    "Liberal Policies: " + ("").join(lib_track_str))
                    await self.bot.send_message(self.channel,
                    "Fascist Policies: " + ("").join(fas_track_str))
                else:
                    await self.bot.send_message(self.channel,
                    "The cards were vetoed")

                if Tracks.Track.win in results:
                    break
                if Tracks.Track.examine in results:
                    await self.bot.send_message(self.channel,"The current president gets to see the next three cards of the deck")
                    await self.examine()
                if Tracks.Track.kill in results:
                    await self.bot.send_message(self.channel,"The current president gets to choose to kill someone")
                    await self.kill()
                if Tracks.Track.veto in results:
                    await self.bot.send_message(self.channel,"The veto power has been unlocked")
                    self.veto = True
                if Tracks.Track.inspect in results:
                    await self.bot.send_message(self.channel,"The current president gets to inspect one person")
                    await self.inspect()
                if Tracks.Track.election in results:
                    await self.bot.send_message(self.channel,"The current president gets to hold a Special Election")
                    self.specialElection = 1

                if self.hitler.dead:
                    break

            if self.hitler.dead or self.libtrack.policies>=5:
                await self.bot.send_message(self.channel,"The Liberals have won")
            else:
                await self.bot.send_message(self.channel,"The Fascists have won")

    async def tellRoles(self, player, x):
        await player.tell("If you don't know the rules, read them here: http://secrethitler.com/assets/Secret_Hitler_Rules.pdf")
        await player.tell(Tracks.Track.Track_key)
        if player.fascist:
            await player.tell("You are a ***fascist***")
            await player.tell("All of the Fascists are")
            for p in self.players.players:
                if p.fascist:
                    await player.tell(p.username)
        elif player.hitler:
            await player.tell("You are ***Hitler***")
            if self.noOfPlayers <=6:
                await player.tell("All of the Fascists are")
                for p in self.players.players:
                    if p.fascist:
                        await player.tell(p.username)
        else:
            await player.tell("You are a ***liberal***")
        del x[0]

    async def vote(self):
        yes=[]
        no=[]
        alive_players = [p for p in self.players.players if not p.dead]
        x = [False]*len(alive_players)
        for player in alive_players:
            # msg = await get_vote(player)
            asyncio.ensure_future(player.get_vote(yes,no,x))
            # print(msg)
        while len(x)!=0:
            await asyncio.sleep(1)
        return yes, no

    async def examine(self):
        await self.players.find_president().tell("The top 3 cards of the deck are:")
        cards = self.deck.peak(3)
        for card in ["Liberal" if c == "L" else "Fascist" for c in cards]:
                    await self.players.find_president().tell(card)

    async def kill(self):
        approved = [player.username for player in self.players.players if not (player.president or player.dead)]
        killUsername = await self.players.find_president().request("kill",
            approved,
            print_allowed = True)
        killed = self.players.find_player(killUsername)
        killed.dead = True
        await self.bot.send_message(self.channel,killUsername + " was killed.")

    async def inspect(self):
        approved = [player.username for player in self.players.players if not (player.president or player.dead)]
        inspectUsername = await self.players.find_president().request("inspect",
            approved,
            print_allowed = True)
        inspected = self.players.find_player(inspectUsername)
        if inspected.hitler or inspected.fascist:
            await self.players.find_president().tell("The person you investigated was a fascist")
        else:
            await self.players.find_president().tell("The person you investigated was a liberal")
