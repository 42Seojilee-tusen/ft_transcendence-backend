from chat.gamegroup import GameGroup
from chat.tournamentgamegroup import TournamentGameGroup

import logging
logger = logging.getLogger('chat') 
class MatchManager():
    waiting_channels = []

    # 대기열 추가
    def add_waiting(self, channel_name, user):
        
        self.waiting_channels.append({
            'channel_name': channel_name,
            'user': user
        })

    # 대기열 삭제
    def del_waiting(self, channel_name):
        for i, user in enumerate(self.waiting_channels):
            if user['channel_name'] == channel_name:
                del self.waiting_channels[i]
                break

    # 매칭시켜주는 로직
    # 매칭될 유저가 없으면 대기열에 추가 후 None 반환
    # 있으면 GameGroup객체 반환
    def matching2(self, channel2, user2):
        # 매칭 로직
        if len(self.waiting_channels) < 1:
            self.add_waiting(channel2, user2)
            return None
        waiting_channel1 = self.waiting_channels.pop(0)
        channel1 = waiting_channel1['channel_name']
        user1 = waiting_channel1['user']
        channels = [channel1, channel2]
        users = [user1, user2]
        game_group = GameGroup(channels, users)
        return game_group

    def matching4(self, channel4, user4):
        # 매칭 로직
        if len(self.waiting_channels) < 3:
            self.add_waiting(channel4, user4)
            return None
        waiting_channel1 = self.waiting_channels.pop(0)
        channel1 = waiting_channel1['channel_name']
        user1 = waiting_channel1['user']
        waiting_channel2 = self.waiting_channels.pop(0)
        channel2 = waiting_channel2['channel_name']
        user2 = waiting_channel2['user']
        waiting_channel3 = self.waiting_channels.pop(0)
        channel3 = waiting_channel3['channel_name']
        user3 = waiting_channel3['user']
        channels = [channel1, channel2, channel3, channel4]
        users = [user1, user2, user3, user4]
        logger.debug("매칭 완료!")
        logger.debug(channels)
        logger.debug("매칭 완료!")
        game_group = TournamentGameGroup(channels, users)
        return game_group