import sys
import requests
import json
from datetime import datetime
from extensions import registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_TYPES
from maltego_trx.transform import DiscoverableTransform


class DiscordSensor:

    BASE_URL = "https://discord-sensor.com/api/tracker"

    @staticmethod
    def get_friends(ds_id, page=0, limit=20):
        url = f"https://discord-sensor.com/api/tracker/get-friends/{ds_id}?page={page}"

        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}

            data = response.json()
            if not data.get('success', False):
                return {"error": "API returned success=false"}

            return data
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _format_duration(seconds):
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes} мин {secs} сек"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours} ч {minutes} мин {secs} сек"

    @staticmethod
    def _format_date(date_str):
        if not date_str:
            return "Неизвестно"
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except:
            return date_str

    @staticmethod
    def get_user_info(username):
        url = f"{DiscordSensor.BASE_URL}/get-user-info?content={username}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_servers(ds_id):
        url = f"{DiscordSensor.BASE_URL}/get-mutual-guilds/{ds_id}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_nicknames(ds_id, max_pages=3):
        all_nicknames = []
        for page in range(max_pages):
            url = f"{DiscordSensor.BASE_URL}/get-nicknames/{ds_id}?page={page}"
            try:
                response = requests.get(url, timeout=15)
                if response.status_code != 200:
                    break
                data = response.json()
                if not data.get('success', False):
                    break
                all_nicknames.extend(data.get('nicknames', []))
                if not data.get('hasNextPage', False):
                    break
            except:
                break
        return {"total": len(all_nicknames), "nicknames": all_nicknames}

    @staticmethod
    def get_events(ds_id, limit=20):
        url = f"https://discord-sensor.com/api/users/get-latest-events/{ds_id}?subTab=server_history&limit={limit}&page=1"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_voice_history(ds_id, limit=20):
        url = f"https://discord-sensor.com/api/users/get-latest-events/{ds_id}?subTab=voice_history&limit={limit}&page=1"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}
            return response.json()
        except Exception as e:
            return {"error": str(e)}


@registry.register_transform(
    display_name="FullDiscordOSINT",
    input_entity="maltego.Phrase",
    description="Полный сбор информации о пользователе Discord: профиль, серверы, никнеймы, история, войсы",
    output_entities=["maltego.Phrase", "maltego.Affiliation", "maltego.Person"]
)
class FullDiscordOSINT(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        query = request.Value.strip().strip('"')
        response.addUIMessage("==================================================")
        response.addUIMessage(f"[*] Поиск по: {query}")

        is_id = query.isdigit()
        ds_id = None
        user_data = None

        if is_id:
            ds_id = query
            response.addUIMessage(f"[+] Discord ID: {ds_id}")
            user_data = DiscordSensor.get_user_info(ds_id)
            if "error" in user_data:
                response.addUIMessage(f"[-] Ошибка API: {user_data['error']}", UIM_TYPES['partial'])
                return
        else:
            response.addUIMessage(f"[*] Ищем username: {query}")
            user_data = DiscordSensor.get_user_info(query)
            if "error" in user_data:
                response.addUIMessage(f"[-] Ошибка API: {user_data['error']}", UIM_TYPES['partial'])
                return

            if user_data and user_data.get('user_id'):
                ds_id = user_data.get('user_id')
                response.addUIMessage(f"[+] Найден ID: {ds_id}")
            elif user_data and user_data.get('actual_name'):

                response.addUIMessage(f"[*] Получаем полные данные...")
                ds_id = None
            else:
                response.addUIMessage("[-] Пользователь не найден", UIM_TYPES['partial'])
                return

        if user_data and not isinstance(user_data, dict) or "error" not in user_data:
            cls._add_user_profile(response, user_data, ds_id or query)

        if ds_id:
            response.addUIMessage("[*] Получение серверов...")
            servers_data = DiscordSensor.get_servers(ds_id)
            cls._add_servers(response, servers_data)

            response.addUIMessage("[*] Получение никнеймов...")
            nicknames_data = DiscordSensor.get_nicknames(ds_id)
            cls._add_nicknames(response, nicknames_data)

            response.addUIMessage("[*] Получение истории...")
            events_data = DiscordSensor.get_events(ds_id)
            cls._add_events(response, events_data)

            response.addUIMessage("[*] Получение голосовой истории...")
            voice_data = DiscordSensor.get_voice_history(ds_id)
            cls._add_voice_history(response, voice_data)

            response.addUIMessage("[*] Получение списка друзей...")
            friends_data = DiscordSensor.get_friends(ds_id)
            cls._add_friends(response, friends_data, ds_id)
        else:
            response.addUIMessage("[!] Не удалось получить ID для дополнительных данных", UIM_TYPES['partial'])

        response.addUIMessage("[+] Готово!")
        response.addUIMessage("==================================================")

    @classmethod
    def _add_user_profile(cls, response, data, identifier):
        user_id = data.get('user_id', identifier)
        username = data.get('actual_name', data.get('display_name', identifier))

        user_entity = response.addEntity("maltego.Person", username)
        user_entity.addProperty("discord_id", displayName="Discord ID", value=user_id)
        user_entity.addProperty("display_name", displayName="Отображаемое имя", value=data.get('display_name', ''))
        user_entity.addProperty("status", displayName="Статус", value=data.get('status', ''))
        user_entity.addProperty("gender", displayName="Пол", value=data.get('gender', 'Не указан'))

        voice_seconds = data.get('time_in_voice', 0)
        if voice_seconds:
            user_entity.addProperty("voice_time", displayName="Время в войсах",
                                    value=DiscordSensor._format_duration(voice_seconds))

        total_messages = data.get('total_messages', 0)
        user_entity.addProperty("total_messages", displayName="Всего сообщений", value=str(total_messages))

    @classmethod
    def _add_servers(cls, response, data):
        if "error" in data:
            response.addUIMessage(f"[-] Ошибка серверов: {data['error']}", UIM_TYPES['debug'])
            return

        servers = data.get('guild_list', [])

        if not servers:
            response.addUIMessage("[-] Серверы не найдены", UIM_TYPES['debug'])
            return

        response.addUIMessage(f"[+] Найдено серверов: {len(servers)}")

        for server in servers:
            server_name = server.get('name', 'Unknown')
            status = "+" if not server.get('left') else ""

            entity = response.addEntity("maltego.Affiliation", f"{status} {server_name}")
            entity.addProperty("server_id", displayName="Server ID", value=str(server.get('id', '')))
            entity.addProperty("status", displayName="Status",
                               value="На сервере" if not server.get('left') else "Покинул")

            member_count = server.get('member_count', 0)
            try:
                member_count = int(member_count)
            except (ValueError, TypeError):
                member_count = 0
            entity.addProperty("member_count", displayName="Участников", value=str(member_count))

            voice_members = server.get('voice_member_count', 0)
            try:
                voice_members = int(voice_members)
            except (ValueError, TypeError):
                voice_members = 0
            entity.addProperty("voice_members", displayName="В войсе", value=str(voice_members))

            voice_seconds = server.get('voice_seconds', 0)
            try:
                voice_seconds = int(voice_seconds)
            except (ValueError, TypeError):
                voice_seconds = 0

            if voice_seconds > 0:
                hours = voice_seconds // 3600
                minutes = (voice_seconds % 3600) // 60
                entity.addProperty("voice_time", displayName="Время в войсе", value=f"{hours}ч {minutes}м")

    @classmethod
    def _add_nicknames(cls, response, data):
        nicknames = data.get('nicknames', [])

        if not nicknames:
            response.addUIMessage("[-] История никнеймов не найдена", UIM_TYPES['debug'])
            return

        response.addUIMessage(f"[+] Найдено никнеймов: {len(nicknames)}")

        for nick in nicknames:
            nick_value = nick.get('nickname', 'Unknown')
            guild_name = nick.get('guild', {}).get('name', 'Unknown')

            entity = response.addEntity("maltego.Phrase", nick_value)
            entity.addProperty("server", displayName="Сервер", value=guild_name)
            entity.addProperty("server_id", displayName="ID сервера", value=str(nick.get('guild', {}).get('id', '')))

            if nick.get('time'):
                formatted_time = DiscordSensor._format_date(nick.get('time'))
                entity.addProperty("changed_at", displayName="Изменен", value=formatted_time)

    @classmethod
    def _add_events(cls, response, data):
        events = data.get('results', [])

        if not events:
            response.addUIMessage("[-] История событий не найдена", UIM_TYPES['debug'])
            return

        response.addUIMessage(f"[+] Найдено событий: {len(events)}")

        for event in events:
            event_type = "ПРИСОЕДИНИЛСЯ" if event.get('type') else "ПОКИНУЛ"
            guild_name = event.get('guild_name', 'Unknown')
            timestamp = DiscordSensor._format_date(event.get('timestamp', ''))

            entity = response.addEntity("maltego.Phrase", f"{event_type}: {guild_name}")
            entity.addProperty("event_type", displayName="Тип", value=event_type)
            entity.addProperty("guild_name", displayName="Сервер", value=guild_name)
            entity.addProperty("guild_id", displayName="ID сервера", value=str(event.get('guild_id', '')))
            entity.addProperty("timestamp", displayName="Дата", value=timestamp)

    @classmethod
    def _add_voice_history(cls, response, data):
        sessions = data.get('results', [])

        if not sessions:
            response.addUIMessage("[-] История голосовых сессий не найдена", UIM_TYPES['debug'])
            return

        total_duration = sum(s.get('voice_duration', 0) for s in sessions)
        response.addUIMessage(
            f"[+] Найдено голосовых сессий: {len(sessions)}, общее время: {DiscordSensor._format_duration(total_duration)}")

        for session in sessions:
            guild = session.get('guild_name', 'Unknown')
            channel = session.get('channel_name', 'Unknown')
            duration = DiscordSensor._format_duration(session.get('voice_duration', 0))
            join_time = DiscordSensor._format_date(session.get('join_timestamp', ''))
            leave_time = DiscordSensor._format_date(session.get('leave_timestamp', ''))

            entity = response.addEntity("maltego.Phrase", f"🎤 {guild} → #{channel}")
            entity.addProperty("guild", displayName="Сервер", value=guild)
            entity.addProperty("guild_id", displayName="ID сервера", value=str(session.get('guild_id', '')))
            entity.addProperty("channel", displayName="Канал", value=channel)
            entity.addProperty("channel_id", displayName="ID канала", value=str(session.get('channel_id', '')))
            entity.addProperty("duration", displayName="Длительность", value=duration)
            entity.addProperty("joined", displayName="Вошел", value=join_time)
            entity.addProperty("left", displayName="Вышел", value=leave_time)

    @classmethod
    def _add_friends(cls, response, data, ds_id):
        if "error" in data:
            response.addUIMessage(f"[-] Ошибка получения друзей: {data['error']}", UIM_TYPES['debug'])
            return

        friends_data = data.get('friends', {})
        friends_list = friends_data.get('records', [])
        total_friends = friends_data.get('totalFriends', 0)

        if not friends_list:
            response.addUIMessage("[-] Друзья не найдены", UIM_TYPES['debug'])
            return

        response.addUIMessage(f"[+] Найдено друзей: {total_friends}")

        for friend in friends_list:
            friend_id = friend.get('friendId', '')
            friend_username = friend.get('username', 'Unknown')
            friend_avatar = friend.get('avatar', '')

            entity = response.addEntity("maltego.Person", friend_username)
            entity.addProperty("discord_id", displayName="Discord ID", value=friend_id)
            entity.addProperty("username", displayName="Username", value=friend_username)

            if friend_avatar:
                entity.addProperty("avatar", displayName="Аватар", value=friend_avatar)

            online_duration = friend.get('friends_online_duration', 0)
            try:
                online_duration = int(online_duration)
            except (ValueError, TypeError):
                online_duration = 0

            if online_duration > 0:
                hours = online_duration // 3600
                minutes = (online_duration % 3600) // 60
                entity.addProperty("online_time", displayName="Время онлайн", value=f"{hours}ч {minutes}м")

            last_online = friend.get('last_friends_online', '')
            if last_online:
                formatted_date = DiscordSensor._format_date(last_online)
                entity.addProperty("last_online", displayName="Последний онлайн", value=formatted_date)

            entity.addProperty("relation", displayName="Связь", value="Друн")
            entity.addProperty("source_id", displayName="ID пользователя", value=ds_id)

        mutual_friends = data.get('mutualFriends', [])
        if mutual_friends:
            response.addUIMessage(f"[+] Общих друзей: {len(mutual_friends)}")

            for friend in mutual_friends:
                friend_username = friend.get('username', 'Unknown')
                friend_id = friend.get('friendId', '')

                entity = response.addEntity("maltego.Person", f"{friend_username}")
                entity.addProperty("discord_id", displayName="Discord ID", value=friend_id)
                entity.addProperty("relation", displayName="Связь", value="Общий друн")
                entity.addProperty("source_id", displayName="ID пользователя", value=ds_id)