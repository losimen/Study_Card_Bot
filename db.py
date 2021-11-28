import sqlite3
from operator import itemgetter

import uuid

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):

        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id, name):
        """Добавляем юзера в базу"""
        if self.user_exists(user_id):
            print("User {0} exist".format(user_id))
        else:
            self.cursor.execute("INSERT OR IGNORE INTO `users` (`id`,`name`) VALUES (?, ?)", (user_id, name))
        return self.conn.commit()

    def update_score(self, user_id, score):
        result = self.cursor.execute("SELECT * FROM `users` WHERE `id` = ?", (user_id,))
        for r in result:
            score += r[1]
        self.cursor.execute("UPDATE `users` set `score` = ? where id = ?", (score, user_id))

        return self.conn.commit()

    def score_results(self):
        result = self.cursor.execute("SELECT * FROM users")
        new_array = [[]]
        i = 0
        for r in result:
            new_array[i].append(r[2])
            new_array[i].append(r[1])
            new_array.append([])
            i += 1
        new_array.remove([])
        new_array = sorted(new_array, key = itemgetter(1))
        new_array.reverse()

        return new_array

    def update_busy(self, user_id, busy):
        self.cursor.execute("UPDATE `users` set `inGame` = ? where id = ?", (busy, user_id))
        return self.conn.commit()

    def get_busy(self, user_id):
        result = self.cursor.execute("SELECT `inGame` FROM `users` WHERE `id` = ?", (user_id,))
        return bool(result.fetchall()[0][0])

    def token_exists(self, token):
        result = self.cursor.execute("SELECT * FROM `room` WHERE `token` = ?", (token,))
        return bool(len(result.fetchall()))

    def create_room(self, user_id):
        if not self.get_busy(user_id):
            token = uuid.uuid4().hex[:5]
            if self.token_exists(token):
                print("Token {0} exist".format(token))
                self.create_room()
            else:
                self.update_busy(user_id, 1)
                result = self.cursor.execute("INSERT INTO `room` (`token`,`user_1_id`) VALUES (?, ?)", (token, user_id))
                self.conn.commit()
                return token
        else:
            print(f"User {user_id} exist in room")
            return 0

    def add_user_to_room(self, token, user_id):
        if self.token_exists(token):
            if self.user_exists(user_id):
                if not self.get_busy(user_id):
                    self.update_busy(user_id, 1)
                    result = self.cursor.execute("UPDATE `room` set `user_2_id` = ? where token = ?", (user_id, token))
                    self.conn.commit()
                    return 1
                else:
                    print(f"User {user_id} exist in room")
            else:
                print(f"No such user {user_id}")
        else:
            print(f"No such token {token}")
            return 0

    def update_busy_in_room(self, token, state):
        result = self.cursor.execute("SELECT * FROM `room` WHERE `token` = ?", (token,))
        for r in result:
            self.update_busy(r[1], state)
            self.update_busy(r[2], state)

    def delete_room(self, token):
        if self.token_exists(token):
            self.update_busy_in_room(token, 0)
            self.cursor.execute("DELETE FROM `room` WHERE `token` = ?", (token,))
            self.conn.commit()
            return 1
        else:
            print("No such token {0}".format(token))
            return 0

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()