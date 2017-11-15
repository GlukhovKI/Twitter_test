#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from math import ceil
import twitter
import time
from datetime import datetime, timedelta
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf8')

''' Указываем путь поиска модулей '''
path = os.getcwd()
sys.path.append(path)

try:
    '''Файл конфигурации'''
    config_ini = ConfigParser.RawConfigParser()
    config_ini.read(path + "/config.ini")
except:
    print 'Config file не найден'
    config_ini = None


def logs_file(data):

    if logging == 'True':
        time_now = datetime.now()

        with open(logs_file_name, 'a') as file:
            file.write(str(time_now) + '\n' + data + '\n\n')


def errors_file(data):

    if errors == 'True':
        time_now = datetime.now()

        with open(errors_file_name, 'a') as file:
            file.write(str(time_now) + '\n' + str(data) + '\n\n')


def last_ids_get(friendships):
    last_tweet_ids = {friendship: 0 for friendship in friendships}

    with open(last_ids_file_name, 'w+') as file:
        last_tweet_file = file.read()

        if last_tweet_file:
            last_tweet_lines = last_tweet_file.splitlines()

            for line in last_tweet_lines:

                if line:
                    screen_name, tweet_id = line.split(' ')

                    if screen_name not in last_tweet_ids:
                        last_tweet_ids[screen_name] = tweet_id

                    elif not last_tweet_ids[screen_name]:
                        last_tweet_ids[screen_name] = tweet_id
                        logs_file('Добавили в массив id последнего твита от {}'.format(screen_name))
    return last_tweet_ids


def last_ids_put(friendship, tweet_id):

    file = open(last_ids_file_name, 'r')
    last_tweet_file = file.read()
    file.close()

    if last_tweet_file:
        last_tweet_lines = last_tweet_file.splitlines()
        screen_name_found = False

        for i, line in enumerate(last_tweet_lines):
            screen_name = line.split(' ')[0]

            if screen_name == friendship:
                last_tweet_lines[i] = ' '.join([friendship, str(tweet_id)])
                file = open(last_ids_file_name, 'w')
                file.write('\n'.join(last_tweet_lines))
                file.close()
                screen_name_found = True
                break

        if not screen_name_found:
            file = open(last_ids_file_name, 'a')
            file.write(' '.join([friendship, str(tweet_id)]) + '\n')
            file.close()
    else:
        file = open(last_ids_file_name, 'a')
        file.write(' '.join([friendship, str(tweet_id)]) + '\n')
        file.close()
    return


if __name__ == '__main__':

    if config_ini:

        ''' Подключаеся к Twitter api '''
        consumer_key = config_ini.get("api", "consumer_key")
        consumer_secret = config_ini.get("api", "consumer_secret")
        access_token_key = config_ini.get("api", "access_token_key")
        access_token_secret = config_ini.get("api", "access_token_secret")

        ''' Логирование '''
        logging = config_ini.get("logs", "file_logging")
        errors = config_ini.get("logs", "file_errors")

        ''' Список твиттов '''
        friendships = config_ini.get("api", "friendships")
        friendships = [friendship for friendship in friendships.split(' ')]

        ''' Имена файлов данных '''
        main_file_name = config_ini.get("file_names", "main_file_name")
        last_ids_file_name = config_ini.get("file_names", "last_ids_file_name")
        errors_file_name = config_ini.get("file_names", "errors_file_name")
        logs_file_name = config_ini.get("file_names", "logs_file_name")

        api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token_key,
                          access_token_secret=access_token_secret,
                          sleep_on_rate_limit=True)

        logs_file('Подключились к api')

        try:
            ''' Узнаем существующие подписки, если пользователь не подписан на желаемые аккаунты, то подписываемся'''

            lookup_friendship = api.LookupFriendship(screen_name=friendships)
            existence_friendship = [friendship.screen_name.lower() for friendship in lookup_friendship]

            last_tweet_ids = last_ids_get(friendships)
            logs_file('Подписки получены')

            for friendship in friendships:

                if friendship.lower() not in existence_friendship:

                    api.CreateFriendship(screen_name=friendship)
                    logs_file('Подписались на {}'.format(friendship))

                from_id = None

                ''' Если в файле не сохранен последний id для точки отсчета, то берем последний твитт '''

                if not last_tweet_ids[friendship]:

                    status = api.GetUserTimeline(screen_name=friendship, count=1)
                    logs_file('Находим последний твит для точки отсчета screen_name = {}'.format(friendship))

                    if status:
                        last_tweet_ids[friendship] = status[0].id

            logs_file('Последние твитты по id проверяны')

        except Exception as error:
            errors_file('Подписки и сохранение последнего id: ' + str(error))
            existence_friendship = []

        try:
            ''' Узнаем ограничение на количество запросов в Twitter для приложения
                и вычесляем задержку между "кругами" прослушки новых твиттов'''

            # TODO: api возвращает лимит запросов для user auth, нужен лимит запросов для app auth

            limit = api.CheckRateLimit(url='https://api.twitter.com/1.1/statuses/user_timeline.json').limit
            delay = ceil(900 / limit * len(friendships))
            logs_file('Задержка между "кругом" равна {}'.format(delay))

        except Exception as error:
            delay = None
            errors_file('Лимит: ' + str(error))

        if friendships and delay:

            while True:

                try:
                    for friendship in friendships:

                        if last_tweet_ids[friendship]:
                            from_id = last_tweet_ids[friendship]
                        else:
                            from_id = None

                        statuses = api.GetUserTimeline(screen_name=friendship, since_id=from_id)

                        if statuses:

                            statuses.reverse()  # Возвращаемые твиты идут не в хронологическом порядке

                            for status in statuses:

                                ''' Форматируем дату твитта со сдвигом часовых поясов'''
                                # FIXME: type(datetime) -> type(date)

                                created_time = status.created_at
                                created_time = datetime.strptime(created_time, "%a %b %d %H:%M:%S +0000 %Y")
                                delta = timedelta(hours=3)
                                new_created_time = created_time + delta
                                new_created_time = datetime.strftime(new_created_time, "%a %b %d %H:%M:%S +0300 %Y")

                                tweet_id = status.id
                                user_screen_name = status.user.screen_name

                                last_tweet_ids[friendship] = tweet_id

                                ''' Записываем нужные данные в файл '''

                                with open(main_file_name, 'a') as file:
                                    file.write(', '.join([new_created_time, user_screen_name]) + '\n')

                                ''' Записываем id последнего твитта, для возможности перезапуска программы '''

                                last_ids_put(friendship, tweet_id)

                    time.sleep(delay)

                except Exception as error:
                    errors_file('Неизвестная ошибка: ' + str(error))
                    time.sleep(60)

