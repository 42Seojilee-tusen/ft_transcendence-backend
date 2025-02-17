from chat.gamegroup import GameGroup

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
    def matching(self, channel2, user2):
        # 매칭 로직
        if len(self.waiting_channels) <= 0:
            self.add_waiting(channel2, user2)
            return None
        user1 = self.waiting_channels.pop(0)
        channel1 = user1['channel_name']
        user1 = user1['user']
        game_group = GameGroup(channel1, channel2, user1, user2)
        return game_group