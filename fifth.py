from flask import Flask, request
import logging
import json
import random  # import all things we need

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)  # logging

sessionStorage = {} # для кнопок
sessionDate = {}  # для нужной информации
best_phrases = ['Ты молодец', 'Ты сможешь! Осталось чуть-чуть', 'Давай!', 'Держись!', 'Ничто не достигается без усилий',
                'Я верю в тебя', 'Я знаю, ты сможешь преодолеть себя', 'Каждое усилие еще один шаг к победе',
                'Делай сколько можешь, завтра сможешь ещё больше', 'Победи себя и ты победитель']
# фразы нужны будут потом

warm_up = ['1540737/5c0d70d149bd986d48a6'] # ссылка на картинку


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)  # main function
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']  # initializate user id
    if req['session']['new']:  # if dialog with person is new
        res['response'][
            'text'] = 'Привет! Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                      ' количество упражнений, время выполнения каждого и количество подходов. Если ты' \
                      ' захочешь выйти просто скажи "хватит". Начнем?:)'
        res['response']['tts'] = 'Привет! Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                 'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                 'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                 'скажи хватит. sil <[500]> Начнем?'  # message for user
        sessionDate[user_id] = {
            'new_training': None,
            'ex_count': None,
            'time_of_ex': None,
            'rounds': None,
            'right': None,
            'training_started': False
        }
        sessionStorage[user_id] = {  # dict for buttons
            'suggests': [
                "ДА!",
                "Нет",
                "Конечно!",
            ]
        }
        sessionDate[user_id]['exercizes'] = []
        res['response']['buttons'] = get_suggests(user_id)  # get button's json in correct form
        return

    if sessionDate[user_id]['new_training'] is None:
        if req['request']['original_utterance'].lower() in ['нет', 'не хочу', 'неа', 'нет конечно', 'не хочу']:
            res['response']['text'] = 'Жду вас на следующей тренировке:)'
            res['response']['tts'] = 'Жд+у в+ас н+а сл+едующей тренир+овочке'
            res['response']['end_session'] = True
            sessionDate[user_id]['new_training'] = req['request']['original_utterance'].lower()
            return
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'да!',
            'да',
            'конечно',
            'конечно!',
            'окей',
            'хорошо',
            "начинаем",
            "начнем",
            "начнём",
            "поехали",
            "погнали",
            "гоу"
        ]:

            sessionStorage[user_id] = {
                'suggests': [
                    '1',
                    '2',
                    "3",
                    '4',
                    "5",
                    '6',
                    "7",
                    '8',
                    '9',
                    '10'
                ]
            }
            res['response']['text'] = 'Сколько будет упражнений?' # текст
            res['response']['tts'] = 'Ск+олько б+удет упражн+ений?' # текст произношения
            res['response']['buttons'] = get_suggests(user_id) # получаем кнопки
            sessionDate[user_id]['new_training'] = req['request']['original_utterance'].lower()
            return

        else:
            if req['request']['original_utterance'].lower() in ['хватит', "Алиса, хватит"]:
                res['response']['text'] = 'Жду тебя на следующей тренировочке'
                res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
                res['response']['end_session'] = True
                return

            if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                                "что ты можешь?", "что ты можешь"]:
                res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                          ' количество упражнений, время выполнения каждого и количество ' \
                                          'подходов. Если ты' \
                                          ' захочешь выйти просто скажи "хватит". Начнем?'
                res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                         'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                         'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                         'скажи хватит. sil <[500]> Начнем?'  # message for user
                sessionStorage[user_id] = {
                    'suggests': [
                        'да!'
                    ]
                }
                res['response']['buttons'] = get_suggests(user_id)
                return
            res['response']['text'] = 'Не расслышала, повтори пожалуйста'
            res['response']['tts'] = 'Не рассл+ышала sil <[350]> повтор+и пож+алуста'
            return
    if sessionDate[user_id]['ex_count'] is None:
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response']['text'] = 'Жду тебя на следующей тренировочке'
            res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
            res['response']['end_session'] = True
            return

        if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                            "что ты можешь?", "что ты можешь"]:
            res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                      ' количество упражнений, время выполнения каждого и количество подходов.' \
                                      ' Если ты' \
                                      ' захочешь выйти просто скажи "хватит". Начнем?'
            res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                     'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                     'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                     'скажи хватит. sil <[500]> Начнем?'  # message for user
            sessionStorage[user_id] = {
                'suggests': [
                    'да!'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                                                            '12',
                                                            '13', '14', '15', '16', '17', '18', '19', '20', '21',
                                                            '22',
                                                            '23', '24', '25', '26', '27', '28', '29', '30', '31',
                                                            '32',
                                                            '33', '34', '35', '36', '37', '38', '39', '40', '41',
                                                            '42',
                                                            '43', '44', '45', '46', '47', '48', '49', '50', '51']:
            res['response']['text'] = 'С какой продолжительностью будет идти каждое упражнение?' \
                                      'Пожалуйста укажите в минутах'
            res['response']['tts'] = 'С как+ой пр+одол ж+ительностью б+удет ид+ти к+аждое упражн+ение? ' \
                                     'Пожалуйста укажите в минутах'
            sessionStorage[user_id] = {
                'suggests': [
                    "0.5 минуты",
                    "1 минута",
                    "1,5 минут",
                    "2 минуты",
                    "3 минуты",
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            ex_count = get_number(req)
            sessionDate[user_id]['ex_count'] = ex_count
            return
        else:
            res['response']['text'] = 'Не расслышала, повтори пожалуйста'
            res['response']['tts'] = 'Не рассл+ышала sil <[350]> повтор+и пож+алуйста'
            return
    if sessionDate[user_id]['time_of_ex'] == None:
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response']['text'] = 'Жду тебя на следующей тренировочке'
            res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
            res['response']['end_session'] = True
            return

        if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                            "что ты можешь?", "что ты можешь"]:
            res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                      ' количество упражнений, время выполнения каждого и количество подходов. ' \
                                      'Если ты' \
                                      ' захочешь выйти просто скажи "хватит". Начнем?'
            res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                     'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                     'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                     'скажи хватит. sil <[500]> Начнем?'  # message for user
            sessionStorage[user_id] = {
                'suggests': [
                    'да!'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in ['0.5 минуты', '1 минута', '1.5 минуты', '2.5 минуты',
                                                            '3.5 минуты','4.5 минуты',
                                                            'полторы минуты', '2 минуты', '3 минуты', '4 минуты',
                                                            '5 минут',
                                                            '6 минут', '7 минут', '8 минут', '9 минут', '10 минут',
                                                            '11 минут', '12 минут', '13 минут', '14 минут', '15 минут',
                                                            '16 минут']:
            res['response']['text'] = 'Сколько будет кругов(сетов, повторов)?'
            res['response']['tts'] = 'Ск+олько б+удет круг+ов?'
            sessionStorage[user_id] = {
                'suggests': [
                    '1',
                    "2",
                    "3",
                    "4",
                    '5',
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            time_of_ex = get_number(req)
            sessionDate[user_id]['time_of_ex'] = time_of_ex
            return
        else:

            res['response']['text'] = 'Не расслышала, повтори пожалуйста'
            res['response']['tts'] = 'Не рассл+ышала sil <[350]> повтор+и пож+алуйста'
            return
    if sessionDate[user_id]['rounds'] == None:
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response']['text'] = 'Жду тебя на следующей тренировочке'
            res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
            res['response']['end_session'] = True
            return

        if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                            "что ты можешь?", "что ты можешь"]:
            res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                      ' количество упражнений, время выполнения каждого и количество подходов. ' \
                                      'Если ты' \
                                      ' захочешь выйти просто скажи "хватит". Начнем?'
            res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                     'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                     'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                     'скажи хватит. sil <[500]> Начнем?'  # message for user
            sessionStorage[user_id] = {
                'suggests': [
                    'да!'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in ['1', '2', '3', '4', '5',
                                                            '6', '7', '8', '9',
                                                            '10', '11', '12']:
            rounds = get_number(req)
            sessionDate[user_id]['rounds'] = rounds
            text = 'Отлично, получается {} упражнений с длительностью {} минут и всего {} цикла, верно?'.format(
                sessionDate[user_id]['ex_count'], sessionDate[user_id]['time_of_ex'], sessionDate[user_id]['rounds'])
            res['response']['text'] = text
            res['response'][
                'tts'] = 'Отл+ично sil <[500]> получ+ается {} упр+ажнений с дл+ительностью {} и всег+о ' \
                         '{} ц+икла sil <[500]> верно?'.format(
                sessionDate[user_id]['ex_count'], sessionDate[user_id]['time_of_ex'], sessionDate[user_id]['rounds'])
            sessionStorage[user_id] = {
                'suggests': [
                    'да',
                    "нет"
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        else:
            res['response']['text'] = 'Не расслышала, повтори пожалуйста'
            res['response']['tts'] = 'Не рассл+ышала sil <[350]> повтор+и пож+алуйста'
            return
    if sessionDate[user_id]['right'] == None:
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response']['text'] = 'Жду тебя на следующей тренировочке'
            res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
            res['response']['end_session'] = True
            return

        if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                            "что ты можешь?", "что ты можешь"]:
            res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                      ' количество упражнений, время выполнения каждого и количество подходов. ' \
                                      'Если ты' \
                                      ' захочешь выйти просто скажи "хватит". Начнем?'
            res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                     'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                     'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                     'скажи хватит. sil <[500]> Начнем?'  # message for user
            sessionStorage[user_id] = {
                'suggests': [
                    'да!'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'да!',
            'да',
            'конечно',
            'конечно!',
            'окей',
            'хорошо',
            "верно"
        ]:
            res['response'][
                'text'] = 'Если готов прямо сейчас начать тренировку, скажи "готов"'
            res['response']['tts'] = 'Если готов прямо сейчас начать тренировку, скажи готов'
            sessionDate[user_id]['right'] = True
            sessionDate[user_id]['training_started'] = False
            sessionDate[user_id]['exercizes'] = 0
            sessionDate[user_id]['round_counter'] = 0
            sessionStorage[user_id] = {
                'suggests': [
                    'готов'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in ['нет', 'не хочу', 'неа', 'нет конечно', 'не хочу']:
            res['response']['text'] = "Хорошо, начинаем заново, сделаем новую тренировку?"
            sessionDate[user_id] = {  # date for code
                'new_training': None,
                'ex_count': None,
                'time_of_ex': None,
                'rounds': None,
                'right': None,
                'training_started': False
            }
            return

        # теперь мы ожидаем ответ на предложение начать.
        # В sessionDate[user_id]['training_started'] хранится True или False в зависимости от того,
        # начал пользователь игру или нет.
    if sessionDate[user_id]['training_started'] == False:
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response']['text'] = 'Жду тебя на следующей тренировочке'
            res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
            res['response']['end_session'] = True
            return

        if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                            "что ты можешь?", "что ты можешь"]:
            res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                      ' количество упражнений, время выполнения каждого и количество подходов. ' \
                                      'Если ты' \
                                      ' захочешь выйти просто скажи "хватит". Начнем?'
            res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                     'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                     'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                     'скажи хватит. sil <[500]> Начнем?'  # message for user
            sessionStorage[user_id] = {
                'suggests': [
                    'да!'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)

            return
        # игра не начата, значит мы ожидаем ответ на предложение сыграть.
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'да!',
            'да',
            'конечно',
            'конечно!',
            'окей',
            'хорошо',
            "верно",
            "готов"
        ]:
            morning_exercises(res, req) # функция разминки
            sessionStorage[user_id] = {
                'suggests': [
                    'готов'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return

        if req['request']['original_utterance'].lower() in ['нет', 'не хочу', 'неа', 'нет конечно',
                                                            'не хочу']:
            res['response']['text'] = "бе, начинаем заново, сделаем новую тренировку?"
            sessionDate[user_id] = {  # date for code
                'new_training': None,
                'ex_count': None,
                'time_of_ex': None,
                'rounds': None,
                'right': None,
                'training_started': False
            }
            return

        else:
            res['response']['text'] = 'Не расслышала, повтори пожалуйста'  # that's okey
            res['response']['tts'] = 'Не рассл+ышала sil <[350]> повтор+и пож+алуйста'
            sessionStorage[user_id] = {
                'suggests': [
                    'да',
                    "нет"
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return

    else:
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response']['text'] = 'Жду тебя на следующей тренировочке'
            res['response']['tts'] = 'Жду тебя на сл+едущей тренир+овочке'
            res['response']['end_session'] = True
            return

        if req['request']['original_utterance'].lower() in ['помощь', 'помоги', "что ты умеешь?", "что ты умеешь",
                                                            "что ты можешь?", "что ты можешь"]:
            res['response']['text'] = 'Я буду следить за твоим временем на тренировках. Надо будет просто указать' \
                                      ' количество упражнений, время выполнения каждого и количество подходов. ' \
                                      'Если ты' \
                                      ' захочешь выйти просто скажи "хватит". Начнем?'
            res['response']['tts'] = 'Я буду след+ить за твоим вр+еменем на тренир+овках. Надо будет' \
                                     'пр+осто указать количество упражнений, время выполнения каждого и ' \
                                     'количество подходов. Если ты захочешь выйти sil <[300]> просто ' \
                                     'скажи хватит. sil <[500]> Начнем?'  # message for user
            sessionStorage[user_id] = {
                'suggests': [
                    'да!'
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'да!',
            'да',
            'конечно',
            'конечно!',
            'окей',
            'хорошо',
            "верно",
            "готов"
        ]:
            # если пользователь согласен, то проверяем не сделал ли он все упражнения уже
            if (sessionDate[user_id]['round_counter'] + 1 == sessionDate[user_id]['rounds']) and (
                    sessionDate[user_id]['exercizes'] + 1 == sessionDate[user_id]['ex_count']):
                last_ex(res, req)
                sessionDate[user_id]['training_started'] = False
                return
            if sessionDate[user_id]['round_counter'] == sessionDate[user_id]['rounds']:
                res['response'][
                    'text'] = 'Ееееей! Тренировка окончена! Мы это сделали! Ты супер! Продолжай так же каждый день'
                res['end_session'] = True
                sessionDate[user_id]['training_started'] = False
                return
            if sessionDate[user_id]['exercizes'] + 1 == sessionDate[user_id]['ex_count']:
                last_ex_of_round(res, req)
                sessionDate[user_id]['round_counter'] += 1
                sessionDate[user_id]['exercizes'] = 0
                sessionStorage[user_id] = {
                    'suggests': [
                        'готов'
                    ]
                }
                res['response']['buttons'] = get_suggests(user_id)
                return
            else:
                # если есть не сделанные упражнения, то продолжаем тренировку
                sessionDate[user_id]['training_started'] = True
                training_exercize(res, req)
                sessionStorage[user_id] = {
                    'suggests': [
                        'готов'
                    ]
                }
                res['response']['buttons'] = get_suggests(user_id)
                return

        if req['request']['original_utterance'].lower() in ['нет', 'не хочу', 'неа', 'нет конечно',
                                                            'не хочу']:
            res['response']['text'] = "Хорошо, начинаем заново, сделаем новую тренировку?"
            res['response']['tts'] = "Хорошо, начинаем заново, сделаем новую тренировку?"
            sessionDate[user_id] = {  # date for code
                'new_training': None,
                'ex_count': None,
                'time_of_ex': None,
                'rounds': None,
                'right': None,
                'training_started': False
            }
            return
        else:
            res['response']['text'] = 'Не расслышала, повтори пожалуйста 249'  # that's okey
            res['response']['tts'] = 'Не рассл+ышала sil <[350]> повтор+и пож+алуйста'
            sessionStorage[user_id] = {
                'suggests': [
                    'да',
                    "нет"
                ]
            }
            res['response']['buttons'] = get_suggests(user_id)


def last_ex_of_round(res, req): # последнее упражнение каждого круга
    user_id = req['session']['user_id']
    phrase1 = random.choice(best_phrases)
    phrase2 = random.choice(best_phrases)
    time2 = sessionDate[user_id]['time_of_ex'] * 60 * 1000 - 20000
    tt = 'sil <[{}]>'.format(time2)
    tts = 'три sil <[1000]> два sil <[1000]> один sil <[1000]> Время пошло sil<[10000]> ' + phrase1 + tt \
          + phrase2 + 'Упражнение окончено. Ты сделал круг. отдохни 20 секунд. 20 sil <[1000]> 19 sil <[1000]> ' \
                      '18 sil <[1000]> 17 sil <[1000]> 16 sil <[1000]> 15 sil <[1000]> 14 sil <[1000]> ' \
                      '13 sil <[1000]> 12 sil <[1000]> 11 sil <[1000]> 10 sil <[1000]> 9 sil <[1000]> ' \
                      '8 sil <[1000]> 7 sil <[1000]>' \
                      ' 6 sil <[1000]> 5 sil <[1000]> 4 sil <[1000]> 3 sil ' \
                      '<[1000]> 2 sil <[1000]> 1 sil <[1000]> Скажи "готов" и ' \
                      'начнем следующее упражнение'
    sessionStorage[user_id] = {
        'suggests': [
            'готов'
        ]
    }
    res['response']['buttons'] = get_suggests(user_id)
    res['response']['tts'] = tts
    res['response']['text'] = 'Время пошло. Ты сделал целый круг. Отдохни 20 секунд. Когда будешь готов скажи "готов" и начнем следующее упражнение'


def last_ex(res, req):#самое последнее упражнение
    user_id = req['session']['user_id']
    res['response']['text'] = 'Осталось последнее упражнение, давай!3 2 1 погнали!            ' \
                              'Ееееей ты молодец тренировка завершена, продолжай в том же духе каждый день'
    phrase1 = random.choice(best_phrases) # рандомные поддерживающие фразы
    phrase2 = random.choice(best_phrases)
    time2 = sessionDate[user_id]['time_of_ex'] * 60 * 1000 - 20000
    tt = 'sil <[{}]>'.format(time2)
    tts = 'Последнее упражнение. три sil <[1000]> два sil <[1000]> один sil <[1000]> ' \
          'Время пошло sil<[10000]> ' + phrase1 + tt \
          + phrase2 + 'Тренировка окончена,<speaker audio="alice-sounds-game-win-1.opus"> ' \
                      'продолжай в том же духе каждый день '
    res['response'][
        'tts'] = tts


def morning_exercises(res, req):  # разминка
    user_id = req['session']['user_id']
    res['response']['card'] = {}
    res['response']['card']['type'] = 'BigImage'
    res['response']['card']['title'] = 'Рекомендую размяться. Как будешь готов, скажи "готов"'
    res['response']['card']['image_id'] = warm_up[0]
    res['response']['text'] = 'Рекомендую размяться. Как будешь готов, скажи готов'
    res['response']['tts'] = 'Рекомендую размяться. Как будешь готов, скажи готов'
    sessionDate[user_id]['training_started'] = True
    sessionStorage[user_id] = {
        'suggests': [
            'готов'
        ]
    }
    res['response']['buttons'] = get_suggests(user_id)


def training_exercize(res, req):#обычное упражнение
    user_id = req['session']['user_id']
    sessionDate[user_id]['exercizes'] += 1
    exez = sessionDate[user_id]['exercizes']
    sessionDate[user_id]['training_started'] = True
    text = 'Время пошло. Когда упражнение закончится, скажи "готов" и начнем следующее упражнение'
    res['response']['text'] = text
    phrase1 = random.choice(best_phrases)
    phrase2 = random.choice(best_phrases)
    time2 = sessionDate[user_id]['time_of_ex'] * 60 * 1000 - 20000
    tt = 'sil <[{}]>'.format(time2)
    tts = 'три sil <[1000]> два sil <[1000]> один sil <[1000]> Время пошло sil<[10000]> ' + phrase1 + tt \
          + phrase2 + 'Упражнение окончено отдохни 8 секунд. 8 sil <[1000]> 7 sil <[1000]>' \
                      ' 6 sil <[1000]> 5 sil <[1000]> 4 sil <[1000]> 3 sil ' \
                      '<[1000]> 2 sil <[1000]> 1 sil <[1000]> Скажи "готов" и ' \
                      'начнем следующее упражнение'
    res['response']['tts'] = tts
    sessionStorage[user_id] = {
        'suggests': [
            'готов'
        ]
    }
    res['response']['buttons'] = get_suggests(user_id)
    return


def get_number(req): # получает число
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            return entity['value']


def get_minute(req):# получает время
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.DATETIME':
            print(entity['value'])
            return entity['value'].get('minute', None)


def get_suggests(user_id):# преобразует кнопки в корректный json
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:]
    ]

    return suggests


if __name__ == '__main__':
    app.run()
