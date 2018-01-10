class Track:
    def __init__(self):
        self.policies = 0

    def policy1(self):
        return [None]

    def policy2(self):
        return [None]

    def policy3(self):
        return [None]

    def policy4(self):
        return [None]

    def policy5(self):
        return [None]

    def policy6(self):
        return [None]

    win = ":trophy:"
    examine = ":spy:"
    kill = ":gun:"
    veto = 3
    inspect = ":mag:"
    election = ":tophat:"
    default = ":white_circle:"
    fascist = ":red_circle:"
    liberal = ":large_blue_circle:"
    Track_key = """
Win = {}
Policy Peek = {}
Execution = {}
Investigate Loyalty = {}
Call Special Election = {}
Nothing = {}
Played Fascist Policy = {}
Played Liberal Ploicy = {}
    """.format(win, examine, kill, inspect, election, default, fascist, liberal)

    def update(self):
        self.policies +=1
        return self.evalpolicy(self.policies)

    def evalpolicy(self,n):
        if n==1:
            return self.policy1()
        elif n==2:
            return self.policy2()
        elif n==3:
            return self.policy3()
        elif n==4:
            return self.policy4()
        elif n==5:
            return self.policy5()
        elif n==6:
            return self.policy6()
        else:
            return [None]

class LiberalTrack(Track):
    def __init__(self):
        Track.__init__(self)
        self.track_string_list = []
        for i in range(1,6):
            emoji = self.evalpolicy(i)[0]
            if emoji == None:
                emoji = Track.default
            self.track_string_list.append(emoji)

    def policy5(self):
        return [Track.win]

class FascistTrack1(Track):
    def __init__(self):
        Track.__init__(self)
        self.track_string_list = []
        for i in range(1,7):
            emoji = self.evalpolicy(i)[0]
            if emoji == None:
                emoji = Track.default
            self.track_string_list.append(emoji)

    def policy3(self):
        return [Track.examine]

    def policy4(self):
        return [Track.kill]

    def policy5(self):
        return [Track.kill, Track.veto]

    def policy6(self):
        return [Track.win]

class FascistTrack2(Track):
    def __init__(self):
        Track.__init__(self)
        self.track_string_list = []
        for i in range(1,7):
            emoji = self.evalpolicy(i)[0]
            if emoji == None:
                emoji = Track.default
            self.track_string_list.append(emoji)

    def policy2(self):
        return [Track.inspect]

    def policy3(self):
        return [Track.election]

    def policy4(self):
        return [Track.kill]

    def policy5(self):
        return [Track.kill, Track.veto]

    def policy6(self):
        return [Track.win]

class FascistTrack3(Track):
    def __init__(self):
        Track.__init__(self)
        self.track_string_list = []
        for i in range(1,7):
            emoji = self.evalpolicy(i)[0]
            if emoji == None:
                emoji = Track.default
            self.track_string_list.append(emoji)

    def policy1(self):
        return [Track.inspect]

    def policy2(self):
        return [Track.inspect]

    def policy3(self):
        return [Track.election]

    def policy4(self):
        return [Track.kill]

    def policy5(self):
        return [Track.kill, Track.veto]

    def policy6(self):
        return [Track.win]
