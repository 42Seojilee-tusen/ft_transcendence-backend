class MatchManager():
    waiting_users = []

	# 대기열 추가
    def add_waiting(self, channel_name, user):
        self.waiting_users.append({
			'channel_name': channel_name,
			'user': user
		})

	# 대기열 삭제
    def del_waiting(self, channel_name):
        for i, user in enumerate(self.waiting_users):
            if user['channel_name'] == channel_name:
                del self.waiting_users[i]

	# 대기열에서 한명 뽑기
    def matching(self):
        if len(self.waiting_users) == 0:
            return None
        user1 = self.waiting_users.pop(0)
        return user1