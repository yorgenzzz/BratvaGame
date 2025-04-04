from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import random

# Устанавливаем размер окна (для теста на ПК, на Android это подстроится)
Window.size = (800, 600)

class BratvaGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # Инициализация статистики игры
        self.game_stats = {
            'total_money_earned': 0,
            'total_money_spent': 0,
            'total_boys_hired': 0,
            'total_fights_won': 0,
            'total_fights_lost': 0,
            'total_weed_bought': 0,
            'total_weed_sold': 0,
            'total_quests_completed': 0
        }

        # Загружаем фоновую музыку
        self.bg_music = SoundLoader.load('sounds/bg_music.mp3')
        if self.bg_music:
            self.bg_music.loop = True
            self.bg_music.play()

        # Загружаем звуки
        self.sounds = {
            'recruit': SoundLoader.load('sounds/build.mp3'),
            'deal': SoundLoader.load('sounds/weed.mp3'),
            'fight': SoundLoader.load('sounds/punch.mp3'),
            'win': SoundLoader.load('sounds/win.mp3'),
            'lose': SoundLoader.load('sounds/lose.mp3'),
            'robbery': SoundLoader.load('sounds/siren.mp3'),
            'casino': SoundLoader.load('sounds/cash.mp3'),
            'meeting': SoundLoader.load('sounds/meet.mp3'),
            'money_fight': SoundLoader.load('sounds/car.mp3'),
            'poker': SoundLoader.load('sounds/poker.mp3'),
            'end_day': SoundLoader.load('sounds/end_day.mp3'),
            'click': SoundLoader.load('sounds/click.mp3'),
            'notification': SoundLoader.load('sounds/cash.mp3')
        }

        # Инициализация игрока
        self.player = {
            'nickname': '',
            'money': 100,
            'weed': 0,
            'boys': 0,
            'max_boys': 3,
            'respect': 10,
            'fear': 10,
            'territory': 1,
            'days': 1,
            'strength': 1
        }

        self.prices = {
            'boy': 50,
            'weed': 50,
            'gym': 20
        }

        self.enemy_districts = [
            {'name': 'Северный', 'power': 5, 'relations': 0},
            {'name': 'Западный', 'power': 5, 'relations': 0},
            {'name': 'Южный', 'power': 5, 'relations': 0}
        ]

        self.cooldowns = {
            'robbery': 0,
            'fight_bet': 0,
            'meeting': 0,
            'poker': 0,
            'money_fight': 0
        }

        # Сюжетные флаги
        self.killers_found = False
        self.killers_decision = None

        # Начальный экран
        self.show_start_screen()

    def show_start_screen(self):
        self.clear_widgets()
        self.background = Image(source='images/start_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

        self.start_label = Label(text='Братва 90-х', font_size=40, color=(1, 0, 0, 1))
        self.add_widget(self.start_label)

        self.nickname_input = TextInput(hint_text='Введи своё погоняло', multiline=False, size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5})
        self.add_widget(self.nickname_input)

        self.start_btn = Button(text='Начать игру', size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5}, on_press=self.start_game)
        self.add_widget(self.start_btn)

    def start_game(self, instance):
        self.sounds['click'].play()
        nickname = self.nickname_input.text.strip()
        if not nickname:
            self.show_popup('Введи погоняло, братишка!')
            return
        self.player['nickname'] = nickname
        self.show_rules_screen()

    def show_rules_screen(self):
        self.clear_widgets()
        self.background = Image(source='images/start_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

        rules_text = (
            'Ты — пацан с района в 90-е, твоя цель — стать самым уважаемым.\n'
            'Набирай братву, зарабатывай бабки, торгуй шмалью, отжимай ларьки, дерись с чужими.\n'
            'Каждый день твоя братва приносит бабки, но цены растут, менты и враги не дремлют.\n'
            'Если бабки кончатся — игра окончена. Всё по-честному, братишка!'
        )
        self.rules_label = Label(text=rules_text, font_size=20, color=(1, 1, 1, 1), halign='center', text_size=(Window.width - 40, None))
        self.add_widget(self.rules_label)

        self.rules_btn = Button(text='Согласен, погнали!', size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5}, on_press=self.show_game_screen)
        self.add_widget(self.rules_btn)

    def show_game_screen(self, instance=None):
        self.clear_widgets()
        self.background = Image(source='images/yard.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

        # Статистика
        self.stats_label = Label(
            text=self.get_stats_text(),
            size_hint=(1, 0.15),
            font_size=18,
            color=(1, 1, 1, 1),
            halign='left',
            valign='top',
            text_size=(Window.width - 20, None)
        )
        self.add_widget(self.stats_label)

        # Кнопки действий
        self.actions_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.recruit_btn = Button(text=f'Нанять пацана ({self.prices["boy"]} руб.)', on_press=self.recruit_boy)
        self.end_day_btn = Button(text='Закончить день', on_press=self.end_day)
        self.stats_btn = Button(text='Общая статистика', on_press=self.show_game_stats)
        self.actions_layout.add_widget(self.recruit_btn)
        self.actions_layout.add_widget(self.end_day_btn)
        self.actions_layout.add_widget(self.stats_btn)
        self.add_widget(self.actions_layout)

        # Магазин
        self.shop_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.buy_weed_btn = Button(text=f'Купить шмаль ({self.prices["weed"]} руб. за 10 г)', on_press=self.buy_weed)
        self.sell_weed_btn = Button(text='Продать шмаль (5 руб. за 1 г)', on_press=self.sell_weed)
        self.shop_layout.add_widget(self.buy_weed_btn)
        self.shop_layout.add_widget(self.sell_weed_btn)
        self.add_widget(self.shop_layout)

        # Казино
        self.casino_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.casino_10_btn = Button(text='Казино (10 руб.)', on_press=lambda x: self.play_casino(10))
        self.casino_50_btn = Button(text='Казино (50 руб.)', on_press=lambda x: self.play_casino(50))
        self.casino_layout.add_widget(self.casino_10_btn)
        self.casino_layout.add_widget(self.casino_50_btn)
        self.add_widget(self.casino_layout)

        # Качалка
        self.gym_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.gym_btn = Button(text=f'Качалка ({self.prices["gym"]} руб.)', on_press=self.train_boys)
        self.gym_layout.add_widget(self.gym_btn)
        self.add_widget(self.gym_layout)

        # Бои
        self.fight_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.fight_btn = Button(text='Драка с врагами', on_press=self.fight_enemy)
        self.bet_fight_btn = Button(text='Ставка на бой (10 руб.)', on_press=self.bet_on_fight)
        self.fight_layout.add_widget(self.fight_btn)
        self.fight_layout.add_widget(self.bet_fight_btn)
        self.add_widget(self.fight_layout)

        # Ограбление
        self.robbery_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.robbery_btn = Button(text='Ограбить ларек (КД: 3 дня)', on_press=self.rob_kiosk)
        self.robbery_layout.add_widget(self.robbery_btn)
        self.add_widget(self.robbery_layout)

        # Сходки
        self.meeting_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.meeting_btn = Button(text='Сходка (КД: 5 дней)', on_press=self.go_to_meeting)
        self.meeting_layout.add_widget(self.meeting_btn)
        self.add_widget(self.meeting_layout)

        # Похерка
        self.poker_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.poker_btn = Button(text='Похерка (КД: 2 дня)', on_press=self.play_poker)
        self.poker_layout.add_widget(self.poker_btn)
        self.add_widget(self.poker_layout)

        # Разборка за бабки
        self.money_fight_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.money_fight_btn = Button(text='Разборка за бабки (КД: 3 дня)', on_press=self.fight_for_money)
        self.money_fight_layout.add_widget(self.money_fight_btn)
        self.add_widget(self.money_fight_layout)

        # Квесты
        self.quest_label = Label(text='Сегодня тихо.', size_hint=(1, 0.1), font_size=16, color=(1, 1, 1, 1))
        self.add_widget(self.quest_label)
        self.quest_buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
        self.add_widget(self.quest_buttons_layout)

        # Статистика дня
        self.day_stats_label = Label(text='', size_hint=(1, 0.1), font_size=16, color=(1, 1, 1, 1))
        self.add_widget(self.day_stats_label)

        self.update_cooldown_buttons()
        self.show_quest()

    def get_stats_text(self):
        return (f'Погоняло: {self.player["nickname"]}\n'
                f'День: {self.player["days"]}\n'
                f'Бабки: {self.player["money"]} руб.\n'
                f'Шмаль: {self.player["weed"]} г\n'
                f'Пацаны: {self.player["boys"]}/{self.player["max_boys"]}\n'
                f'Уважение: {self.player["respect"]}\n'
                f'Страх: {self.player["fear"]}\n'
                f'Территория: {self.player["territory"]}')

    def show_game_stats(self, instance):
        self.sounds['click'].play()
        stats_text = (
            f'Общая статистика игры:\n'
            f'Всего заработано: {self.game_stats["total_money_earned"]} руб.\n'
            f'Всего потрачено: {self.game_stats["total_money_spent"]} руб.\n'
            f'Пацанов нанято: {self.game_stats["total_boys_hired"]}\n'
            f'Боёв выиграно: {self.game_stats["total_fights_won"]}\n'
            f'Боёв проиграно: {self.game_stats["total_fights_lost"]}\n'
            f'Шмали куплено: {self.game_stats["total_weed_bought"]} г\n'
            f'Шмали продано: {self.game_stats["total_weed_sold"]} г\n'
            f'Квестов выполнено: {self.game_stats["total_quests_completed"]}'
        )
        popup = Popup(title='Статистика', content=Label(text=stats_text), size_hint=(0.8, 0.6))
        popup.open()

    def update_stats(self):
        self.stats_label.text = self.get_stats_text()
        self.recruit_btn.text = f'Нанять пацана ({self.prices["boy"]} руб.)'
        self.buy_weed_btn.text = f'Купить шмаль ({self.prices["weed"]} руб. за 10 г)'
        self.gym_btn.text = f'Качалка ({self.prices["gym"]} руб.)'

    def show_popup(self, message):
        popup = Popup(title='Событие', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def animate_button(self, button):
        anim = Animation(size=(button.size[0] * 1.1, button.size[1] * 1.1), duration=0.2) + Animation(size=button.size, duration=0.2)
        anim.start(button)

    def change_money(self, amount):
        if amount > 0:
            self.game_stats['total_money_earned'] += amount
        else:
            self.game_stats['total_money_spent'] += abs(amount)
        self.player['money'] += amount
        if self.player['money'] < 0:
            self.show_popup('Бабки кончились, игра окончена!')
            Clock.schedule_once(lambda dt: self.reset_game(), 2)
            return False
        if amount != 0:
            self.show_popup(f'{"+" if amount > 0 else ""}{amount} руб.')
            self.sounds['notification'].play()
        self.update_stats()
        return True

    def reset_game(self):
        self.player = {
            'nickname': self.player['nickname'],
            'money': 100,
            'weed': 0,
            'boys': 0,
            'max_boys': 3,
            'respect': 10,
            'fear': 10,
            'territory': 1,
            'days': 1,
            'strength': 1
        }
        self.prices = {'boy': 50, 'weed': 50, 'gym': 20}
        self.cooldowns = {'robbery': 0, 'fight_bet': 0, 'meeting': 0, 'poker': 0, 'money_fight': 0}
        self.killers_found = False
        self.killers_decision = None
        self.game_stats = {
            'total_money_earned': 0,
            'total_money_spent': 0,
            'total_boys_hired': 0,
            'total_fights_won': 0,
            'total_fights_lost': 0,
            'total_weed_bought': 0,
            'total_weed_sold': 0,
            'total_quests_completed': 0
        }
        self.show_game_screen()

    def recruit_boy(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.player['boys'] >= self.player['max_boys']:
            self.show_popup('Мест для пацанов больше нет!')
            return
        if self.player['money'] < self.prices['boy']:
            self.show_popup(f'Бабок мало, надо {self.prices["boy"]} руб.!')
            return
        if self.change_money(-self.prices['boy']):
            self.player['boys'] += 1
            self.prices['boy'] = int(self.prices['boy'] * 1.1)
            self.game_stats['total_boys_hired'] += 1
            self.show_popup('Нанял пацана!')
            self.sounds['recruit'].play()
            self.update_stats()

    def buy_weed(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.player['money'] < self.prices['weed']:
            self.show_popup(f'Бабок мало, надо {self.prices["weed"]} руб.!')
            return
        if self.change_money(-self.prices['weed']):
            self.player['weed'] += 10
            self.prices['weed'] = int(self.prices['weed'] * 1.1)
            self.game_stats['total_weed_bought'] += 10
            self.show_popup('Купил 10 г шмали!')
            self.sounds['deal'].play()
            self.update_stats()

    def sell_weed(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.player['weed'] < 1:
            self.show_popup('Шмали нет!')
            return
        amount = min(self.player['weed'], 10)
        self.player['weed'] -= amount
        profit = amount * 5
        self.change_money(profit)
        self.game_stats['total_weed_sold'] += amount
        self.show_popup(f'Продал {amount} г шмали, получил {profit} руб.!')
        self.sounds['deal'].play()
        self.update_stats()

    def play_casino(self, bet):
        self.sounds['click'].play()
        if self.player['money'] < bet:
            self.show_popup(f'Бабок мало, надо {bet} руб.!')
            return
        if self.change_money(-bet):
            if random.random() < 0.3:
                win = int(bet * (random.random() * 2 + 1.5))
                self.change_money(win)
                self.show_popup(f'Выиграл в казино {win} руб.!')
                self.sounds['win'].play()
            else:
                self.show_popup(f'Проиграл в казино, -{bet} руб.!')
                self.sounds['lose'].play()
            self.sounds['casino'].play()

    def train_boys(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.player['boys'] == 0:
            self.show_popup('Пацанов нет!')
            return
        if self.player['money'] < self.prices['gym']:
            self.show_popup(f'Бабок мало, надо {self.prices["gym"]} руб.!')
            return
        if self.change_money(-self.prices['gym']):
            self.player['strength'] += 1
            self.prices['gym'] = int(self.prices['gym'] * 1.1)
            self.show_popup('Пацаны накачались, сила +1!')
            self.sounds['recruit'].play()
            self.update_stats()

    def fight_enemy(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.player['boys'] == 0:
            self.show_popup('Пацанов нет!')
            return
        enemy = random.choice(self.enemy_districts)
        player_power = self.player['boys'] * self.player['strength']
        enemy_power = enemy['power']
        if random.random() < 0.5 + player_power / (player_power + enemy_power):
            money_gain = enemy_power * 5
            self.change_money(money_gain)
            self.player['respect'] = min(100, self.player['respect'] + 5)
            self.player['territory'] += 1
            enemy['power'] = max(1, enemy['power'] - 1)
            self.show_popup(f'Вломил {enemy["name"]} району, +{money_gain} руб., уважение +5, +1 территория!')
            self.sounds['win'].play()
            self.game_stats['total_fights_won'] += 1
        else:
            self.player['boys'] -= 1
            self.player['respect'] = max(0, self.player['respect'] - 3)
            self.show_popup(f'Проиграл {enemy["name"]} району, -1 пацан, уважение -3!')
            self.sounds['lose'].play()
            self.game_stats['total_fights_lost'] += 1
        self.sounds['fight'].play()
        self.update_stats()

    def bet_on_fight(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.cooldowns['fight_bet'] > 0:
            self.show_popup(f'Ставка на бой на кулдауне, осталось {self.cooldowns["fight_bet"]} дней!')
            return
        if self.player['boys'] == 0:
            self.show_popup('Пацанов нет!')
            return
        if self.player['money'] < 10:
            self.show_popup('Бабок мало, надо 10 руб.!')
            return
        if self.change_money(-10):
            enemy = random.choice(self.enemy_districts)
            player_power = self.player['boys'] * self.player['strength']
            enemy_power = enemy['power']
            if random.random() < 0.5 + player_power / (player_power + enemy_power):
                win = random.randint(30, 50)
                self.change_money(win)
                self.player['respect'] = min(100, self.player['respect'] + 3)
                self.show_popup(f'Твой пацан выиграл бой, +{win} руб., уважение +3!')
                self.sounds['win'].play()
                self.game_stats['total_fights_won'] += 1
            else:
                self.show_popup('Твой пацан проиграл бой, -10 руб.!')
                self.sounds['lose'].play()
                self.game_stats['total_fights_lost'] += 1
            self.cooldowns['fight_bet'] = 2
            self.update_cooldown_buttons()
            self.sounds['fight'].play()

    def rob_kiosk(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.cooldowns['robbery'] > 0:
            self.show_popup(f'Ограбление на кулдауне, осталось {self.cooldowns["robbery"]} дней!')
            return
        if self.player['boys'] == 0:
            self.show_popup('Пацанов нет!')
            return
        if random.random() < 0.7:
            money_gain = random.randint(20, 50)
            self.change_money(money_gain)
            self.player['fear'] = min(100, self.player['fear'] + 3)
            self.show_popup(f'Ограбил ларек, +{money_gain} руб., страх +3!')
            self.sounds['win'].play()
        else:
            self.player['respect'] = max(0, self.player['respect'] - 2)
            self.show_popup('Менты спалили, уважение -2!')
            self.sounds['robbery'].play()
        self.cooldowns['robbery'] = 3
        self.update_cooldown_buttons()
        self.update_stats()

    def go_to_meeting(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.cooldowns['meeting'] > 0:
            self.show_popup(f'Сходка на кулдауне, осталось {self.cooldowns["meeting"]} дней!')
            return
        if self.player['boys'] == 0:
            self.show_popup('Пацанов нет!')
            return
        enemy = random.choice(self.enemy_districts)
        if random.random() < 0.6:
            respect_gain = random.randint(5, 10)
            self.player['respect'] = min(100, self.player['respect'] + respect_gain)
            enemy['relations'] += 10
            self.show_popup(f'Сходка прошла удачно, уважение +{respect_gain}!')
            self.sounds['win'].play()
        else:
            self.player['respect'] = max(0, self.player['respect'] - 3)
            enemy['relations'] -= 15
            self.show_popup(f'Сходка закончилась разборкой, уважение -3!')
            self.sounds['lose'].play()
        self.cooldowns['meeting'] = 5
        self.update_cooldown_buttons()
        self.sounds['meeting'].play()
        self.update_stats()

    def play_poker(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.cooldowns['poker'] > 0:
            self.show_popup(f'Похерка на кулдауне, осталось {self.cooldowns["poker"]} дней!')
            return
        if self.player['money'] < 20:
            self.show_popup('Бабок мало, надо 20 руб.!')
            return
        if self.change_money(-20):
            if random.random() < 0.5:
                win = random.randint(30, 70)
                self.change_money(win)
                self.show_popup(f'Выиграл в похерку {win} руб.!')
                self.sounds['win'].play()
            else:
                self.show_popup('Проиграл в похерку, -20 руб.!')
                self.sounds['lose'].play()
            self.cooldowns['poker'] = 2
            self.update_cooldown_buttons()
            self.sounds['poker'].play()

    def fight_for_money(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        if self.cooldowns['money_fight'] > 0:
            self.show_popup(f'Разборка на кулдауне, осталось {self.cooldowns["money_fight"]} дней!')
            return
        if self.player['boys'] == 0:
            self.show_popup('Пацанов нет!')
            return
        if self.player['money'] < 30:
            self.show_popup('Бабок мало, надо 30 руб.!')
            return
        if self.change_money(-30):
            enemy = random.choice(self.enemy_districts)
            player_power = self.player['boys'] * self.player['strength']
            enemy_power = enemy['power']
            if random.random() < 0.5 + player_power / (player_power + enemy_power):
                win = random.randint(50, 100)
                self.change_money(win)
                self.player['respect'] = min(100, self.player['respect'] + 5)
                self.show_popup(f'Выиграл разборку за бабки, +{win} руб., уважение +5!')
                self.sounds['win'].play()
                self.game_stats['total_fights_won'] += 1
            else:
                self.player['respect'] = max(0, self.player['respect'] - 3)
                self.show_popup('Проиграл разборку за бабки, -30 руб., уважение -3!')
                self.sounds['lose'].play()
                self.game_stats['total_fights_lost'] += 1
            self.cooldowns['money_fight'] = 3
            self.update_cooldown_buttons()
            self.sounds['money_fight'].play()
            self.update_stats()

    def update_cooldown_buttons(self):
        self.bet_fight_btn.text = f'Ставка на бой (КД: {self.cooldowns["fight_bet"]} дней)' if self.cooldowns['fight_bet'] > 0 else 'Ставка на бой (10 руб.)'
        self.bet_fight_btn.disabled = self.cooldowns['fight_bet'] > 0
        self.robbery_btn.text = f'Ограбить ларек (КД: {self.cooldowns["robbery"]} дней)' if self.cooldowns['robbery'] > 0 else 'Ограбить ларек (КД: 3 дня)'
        self.robbery_btn.disabled = self.cooldowns['robbery'] > 0
        self.meeting_btn.text = f'Сходка (КД: {self.cooldowns["meeting"]} дней)' if self.cooldowns['meeting'] > 0 else 'Сходка (КД: 5 дней)'
        self.meeting_btn.disabled = self.cooldowns['meeting'] > 0
        self.poker_btn.text = f'Похерка (КД: {self.cooldowns["poker"]} дней)' if self.cooldowns['poker'] > 0 else 'Похерка (КД: 2 дня)'
        self.poker_btn.disabled = self.cooldowns['poker'] > 0
        self.money_fight_btn.text = f'Разборка за бабки (КД: {self.cooldowns["money_fight"]} дней)' if self.cooldowns['money_fight'] > 0 else 'Разборка за бабки (КД: 3 дня)'
        self.money_fight_btn.disabled = self.cooldowns['money_fight'] > 0

    def show_quest(self):
        self.quest_buttons_layout.clear_widgets()
        if self.player['days'] == 5:
            self.handle_day_5_event()
            return
        if self.player['days'] == 10 and not self.killers_found:
            self.handle_day_10_event()
            return

        if random.random() < 0.5:  # 50% шанс на квест
            quest = random.choice(self.quests)
            self.quest_label.text = quest['text'].replace('{nickname}', self.player['nickname'])
            for option in quest['options']:
                btn = Button(text=option['text'], on_press=lambda x, opt=option: self.handle_quest_option(opt))
                self.quest_buttons_layout.add_widget(btn)
        else:
            self.quest_label.text = f'Сегодня тихо, {self.player["nickname"]}.'

    def handle_quest_option(self, option):
        self.sounds['click'].play()
        option['action']()
        self.game_stats['total_quests_completed'] += 1
        self.quest_label.text = 'Квест выполнен.'
        self.quest_buttons_layout.clear_widgets()

    def handle_day_5_event(self):
        self.player['boys'] = 0
        self.player['respect'] = max(0, self.player['respect'] - 10)
        self.player['fear'] = max(0, self.player['fear'] - 10)
        self.show_popup('День 5: Чужие пацаны замочили всю твою братву! Ты остался один, уважение -10, страх -10.')
        self.sounds['lose'].play()
        self.update_stats()
        self.quest_label.text = 'Собери новую братву, чтобы отомстить!'
        self.quest_buttons_layout.clear_widgets()

    def handle_day_10_event(self):
        self.killers_found = True
        self.quest_label.text = 'День 10: Твоя новая братва нашла убийц! Что делать?'
        options = [
            {'text': 'Убить их', 'action': self.kill_killers},
            {'text': 'Пытать их', 'action': self.torture_killers},
            {'text': 'Заставить работать', 'action': self.force_killers_to_work}
        ]
        for option in options:
            btn = Button(text=option['text'], on_press=lambda x, opt=option: self.handle_killers_option(opt))
            self.quest_buttons_layout.add_widget(btn)

    def handle_killers_option(self, option):
        self.sounds['click'].play()
        option['action']()
        self.quest_label.text = 'Решение принято.'
        self.quest_buttons_layout.clear_widgets()

    def kill_killers(self):
        self.player['fear'] = min(100, self.player['fear'] + 20)
        self.player['respect'] = min(100, self.player['respect'] + 10)
        self.show_popup('Убил убийц, страх +20, уважение +10!')
        self.sounds['fight'].play()
        self.killers_decision = 'killed'
        self.update_stats()

    def torture_killers(self):
        self.player['fear'] = min(100, self.player['fear'] + 30)
        self.player['respect'] = max(0, self.player['respect'] - 5)
        money_gain = random.randint(50, 100)
        self.change_money(money_gain)
        self.show_popup(f'Пытал убийц, страх +30, уважение -5, получил {money_gain} руб. с них!')
        self.sounds['fight'].play()
        self.killers_decision = 'tortured'
        self.update_stats()

    def force_killers_to_work(self):
        self.player['boys'] += 2
        self.player['respect'] = min(100, self.player['respect'] + 5)
        self.show_popup('Заставил убийц работать на тебя, +2 пацана, уважение +5!')
        self.sounds['win'].play()
        self.killers_decision = 'forced_to_work'
        self.update_stats()

    def end_day(self, instance):
        self.sounds['click'].play()
        self.animate_button(instance)
        daily_income = 0
        weed_sold = 0
        territory_income = self.player['territory'] * 5

        for _ in range(self.player['boys']):
            boy_income = (self.player['respect'] + self.player['fear']) // 20
            daily_income += boy_income
            if self.player['weed'] > 0:
                sold = min(self.player['weed'], 5)
                self.player['weed'] -= sold
                weed_sold += sold
                daily_income += sold * 5
                self.game_stats['total_weed_sold'] += sold

        if self.killers_decision == 'forced_to_work':
            daily_income += 20  # Убийцы приносят дополнительный доход

        daily_income += territory_income
        self.change_money(daily_income)

        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1

        for enemy in self.enemy_districts:
            enemy['power'] += random.randint(0, 1)

        self.day_stats_label.text = (
            f'Статистика дня {self.player["days"]}:\n'
            f'Пацаны заработали: {daily_income - territory_income - weed_sold * 5} руб.\n'
            f'Продано шмали: {weed_sold} г (+{weed_sold * 5} руб.)\n'
            f'Доход с территории: {territory_income} руб.\n'
            f'Общий доход: {daily_income} руб.'
        )

        self.player['days'] += 1
        self.show_quest()
        self.sounds['end_day'].play()
        self.update_stats()
        self.update_cooldown_buttons()

    quests = [
        {'text': 'Пацан спалился на шмали, что делать, {nickname}?', 'options': [
            {'text': 'Вытащить его', 'action': lambda: self.quest_extract_boy()},
            {'text': 'Забить на него', 'action': lambda: self.quest_ignore_boy()}
        ]},
        {'text': 'Чужой район хочет разборок, {nickname}!', 'options': [
            {'text': 'Выехать на разборки', 'action': lambda: self.fight_enemy(None)},
            {'text': 'Свалить', 'action': lambda: self.quest_flee_from_fight()}
        ]},
        {'text': 'Менты трясут пацана, что делать, {nickname}?', 'options': [
            {'text': 'Занести бабки', 'action': lambda: self.quest_bribe_cops()},
            {'text': 'Вломить менту', 'action': lambda: self.quest_fight_cop()}
        ]},
        {'text': 'Ларек платит меньше, чем надо, {nickname}!', 'options': [
            {'text': 'Нагнать страху', 'action': lambda: self.quest_intimidate_kiosk()},
            {'text': 'Забить', 'action': lambda: self.quest_ignore_kiosk()}
        ]},
        {'text': 'Чужие пацаны хотят отжать район, {nickname}!', 'options': [
            {'text': 'Драться с ними', 'action': lambda: self.fight_enemy(None)},
            {'text': 'Договориться', 'action': lambda: self.quest_negotiate_with_enemies()}
        ]},
        {'text': 'Барыга предлагает шмаль по дешёвке, {nickname}!', 'options': [
            {'text': 'Купить', 'action': lambda: self.quest_buy_cheap_weed()},
            {'text': 'Отказаться', 'action': lambda: self.quest_refuse_cheap_weed()}
        ]},
        {'text': 'Менты устраивают облаву на районе, {nickname}!', 'options': [
            {'text': 'Откупиться', 'action': lambda: self.quest_bribe_cops_raid()},
            {'text': 'Скрыться', 'action': lambda: self.quest_hide_from_raid()}
        ]},
        {'text': 'Пацаны нашли заброшенный склад с бабками, {nickname}!', 'options': [
            {'text': 'Забрать бабки', 'action': lambda: self.quest_take_warehouse_money()},
            {'text': 'Оставить', 'action': lambda: self.quest_leave_warehouse_money()}
        ]},
        {'text': 'Чужие пацаны предлагают замутить сделку, {nickname}!', 'options': [
            {'text': 'Согласиться', 'action': lambda: self.quest_agree_to_deal()},
            {'text': 'Отказаться', 'action': lambda: self.quest_refuse_deal()}
        ]},
        {'text': 'Местный барыга хочет защиты за бабки, {nickname}!', 'options': [
            {'text': 'Согласиться', 'action': lambda: self.quest_protect_dealer()},
            {'text': 'Отказаться', 'action': lambda: self.quest_refuse_protection()}
        ]},
        {'text': 'Чужие пацаны подкинули шмаль с подвохом, {nickname}!', 'options': [
            {'text': 'Взять шмаль', 'action': lambda: self.quest_take_suspicious_weed()},
            {'text': 'Не брать', 'action': lambda: self.quest_refuse_suspicious_weed()}
        ]},
        {'text': 'Менты требуют сдать одного пацана, {nickname}!', 'options': [
            {'text': 'Сдать пацана', 'action': lambda: self.quest_surrender_boy()},
            {'text': 'Отказаться', 'action': lambda: self.quest_refuse_surrender()}
        ]},
        {'text': 'Барыга хочет продать тебе инфу о ментах, {nickname}!', 'options': [
            {'text': 'Купить инфу', 'action': lambda: self.quest_buy_cop_info()},
            {'text': 'Отказаться', 'action': lambda: self.quest_refuse_cop_info()}
        ]},
        {'text': 'Чужие пацаны предлагают союз, {nickname}!', 'options': [
            {'text': 'Согласиться', 'action': lambda: self.quest_form_alliance()},
            {'text': 'Отказаться', 'action': lambda: self.quest_refuse_alliance()}
        ]},
        {'text': 'Пацан украл бабки у братвы, {nickname}!', 'options': [
            {'text': 'Наказать его', 'action': lambda: self.quest_punish_thief()},
            {'text': 'Простить', 'action': lambda: self.quest_forgive_thief()}
        ]}
    ]

    def quest_extract_boy(self):
        cost = 20 + self.player['days'] * 2
        if self.player['money'] < cost:
            self.show_popup(f'Бабок мало, надо {cost} руб.!')
            return
        if self.change_money(-cost):
            self.player['respect'] = min(100, self.player['respect'] + 2)
            self.show_popup(f'Вытащил пацана, -{cost} руб., уважение +2!')
            self.sounds['deal'].play()

    def quest_ignore_boy(self):
        if self.player['boys'] > 0:
            self.player['boys'] -= 1
        self.player['respect'] = max(0, self.player['respect'] - 2)
        self.show_popup('Забил, -1 пацан, уважение -2!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_flee_from_fight(self):
        enemy = random.choice(self.enemy_districts)
        self.player['fear'] = max(0, self.player['fear'] - 2)
        self.player['respect'] = max(0, self.player['respect'] - 1)
        enemy['relations'] -= 5
        self.show_popup('Свалил, страх -2, уважение -1!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_bribe_cops(self):
        cost = 15 + self.player['days'] * 1
        if self.player['money'] < cost:
            self.show_popup(f'Бабок мало, надо {cost} руб.!')
            return
        if self.change_money(-cost):
            self.show_popup(f'Занёс ментам, -{cost} руб.!')
            self.sounds['deal'].play()

    def quest_fight_cop(self):
        if random.random() < 0.4:
            self.player['fear'] = min(100, self.player['fear'] + 5)
            self.player['respect'] = min(100, self.player['respect'] + 3)
            self.show_popup('Вломил менту, страх +5, уважение +3!')
            self.sounds['win'].play()
        else:
            self.player['respect'] = max(0, self.player['respect'] - 2)
            self.show_popup('Менты в ахуе, уважение -2!')
            self.sounds['robbery'].play()
        self.update_stats()

    def quest_intimidate_kiosk(self):
        self.player['fear'] = min(100, self.player['fear'] + 3)
        money_gain = 5 + self.player['days']
        self.change_money(money_gain)
        self.player['respect'] = min(100, self.player['respect'] + 1)
        self.show_popup(f'Нагнал страху, +3 страха, +{money_gain} руб., уважение +1!')
        self.sounds['win'].play()
        self.update_stats()

    def quest_ignore_kiosk(self):
        self.player['respect'] = max(0, self.player['respect'] - 1)
        self.show_popup('Забил, уважение -1!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_negotiate_with_enemies(self):
        cost = 10 + self.player['days'] * 1
        if self.player['money'] < cost:
            self.show_popup(f'Бабок мало, надо {cost} руб.!')
            return
        if self.change_money(-cost):
            enemy = random.choice(self.enemy_districts)
            enemy['relations'] += 5
            self.show_popup(f'Договорился, -{cost} руб.!')
            self.sounds['deal'].play()

    def quest_buy_cheap_weed(self):
        cost = 30 + self.player['days'] * 2
        if self.player['money'] < cost:
            self.show_popup(f'Бабок мало, надо {cost} руб.!')
            return
        if self.change_money(-cost):
            self.player['weed'] += 20
            self.game_stats['total_weed_bought'] += 20
            self.show_popup(f'Купил 20 г шмали за {cost} руб.!')
            self.sounds['deal'].play()
            self.update_stats()

    def quest_refuse_cheap_weed(self):
        self.player['respect'] = max(0, self.player['respect'] - 1)
        self.show_popup('Отказался, уважение -1!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_bribe_cops_raid(self):
        cost = 25 + self.player['days'] * 3
        if self.player['money'] < cost:
            self.show_popup(f'Бабок мало, надо {cost} руб.!')
            return
        if self.change_money(-cost):
            self.show_popup(f'Откупился от ментов, -{cost} руб.!')
            self.sounds['deal'].play()

    def quest_hide_from_raid(self):
        if random.random() < 0.5:
            self.player['fear'] = min(100, self.player['fear'] + 2)
            self.show_popup('Скрылся, страх +2!')
            self.sounds['win'].play()
        else:
            self.player['weed'] = max(0, self.player['weed'] - 10)
            self.show_popup('Менты нашли шмаль, -10 г!')
            self.sounds['robbery'].play()
        self.update_stats()

    def quest_take_warehouse_money(self):
        money_gain = 20 + self.player['days'] * 2
        self.change_money(money_gain)
        self.player['respect'] = min(100, self.player['respect'] + 2)
        self.show_popup(f'Забрал со склада {money_gain} руб., уважение +2!')
        self.sounds['win'].play()
        self.update_stats()

    def quest_leave_warehouse_money(self):
        self.show_popup('Оставил бабки на складе, ничего не получил.')
        self.sounds['lose'].play()

    def quest_agree_to_deal(self):
        if self.player['weed'] < 10:
            self.show_popup('Шмали мало, надо 10 г!')
            return
        self.player['weed'] -= 10
        money_gain = 50 + self.player['days'] * 3
        self.change_money(money_gain)
        self.player['respect'] = min(100, self.player['respect'] + 3)
        self.game_stats['total_weed_sold'] += 10
        self.show_popup(f'Сделка удалась, -10 г шмали, +{money_gain} руб., уважение +3!')
        self.sounds['deal'].play()
        self.update_stats()

    def quest_refuse_deal(self):
        enemy = random.choice(self.enemy_districts)
        enemy['relations'] -= 5
        self.player['respect'] = max(0, self.player['respect'] - 2)
        self.show_popup('Отказался, уважение -2!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_protect_dealer(self):
        money_gain = 15 + self.player['days'] * 2
        self.change_money(money_gain)
        self.player['fear'] = min(100, self.player['fear'] + 3)
        self.show_popup(f'Защитил барыгу, +{money_gain} руб., страх +3!')
        self.sounds['win'].play()
        self.update_stats()

    def quest_refuse_protection(self):
        self.player['respect'] = max(0, self.player['respect'] - 1)
        self.show_popup('Отказался, уважение -1!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_take_suspicious_weed(self):
        if random.random() < 0.5:
            self.player['weed'] += 15
            self.game_stats['total_weed_bought'] += 15
            self.show_popup('Шмаль норм, +15 г!')
            self.sounds['win'].play()
        else:
            self.player['respect'] = max(0, self.player['respect'] - 3)
            self.show_popup('Шмаль палёная, уважение -3!')
            self.sounds['lose'].play()
        self.update_stats()

    def quest_refuse_suspicious_weed(self):
        self.show_popup('Не взял шмаль, ничего не потерял.')

    def quest_surrender_boy(self):
        if self.player['boys'] > 0:
            self.player['boys'] -= 1
            self.player['fear'] = min(100, self.player['fear'] + 3)
            self.player['respect'] = max(0, self.player['respect'] - 3)
            self.show_popup('Сдал пацана, -1 пацан, страх +3, уважение -3!')
            self.sounds['lose'].play()
        else:
            self.show_popup('Пацанов нет, менты в ахуе!')
            self.sounds['robbery'].play()
        self.update_stats()

    def quest_refuse_surrender(self):
        if random.random() < 0.3:
            self.player['fear'] = min(100, self.player['fear'] + 5)
            self.player['respect'] = min(100, self.player['respect'] + 3)
            self.show_popup('Менты отступили, страх +5, уважение +3!')
            self.sounds['win'].play()
        else:
            self.player['weed'] = max(0, self.player['weed'] - 15)
            self.show_popup('Менты конфисковали шмаль, -15 г!')
            self.sounds['robbery'].play()
        self.update_stats()

    def quest_buy_cop_info(self):
        cost = 20 + self.player['days'] * 2
        if self.player['money'] < cost:
            self.show_popup(f'Бабок мало, надо {cost} руб.!')
            return
        if self.change_money(-cost):
            self.player['fear'] = min(100, self.player['fear'] + 5)
            self.show_popup(f'Купил инфу о ментах, -{cost} руб., страх +5!')
            self.sounds['deal'].play()
            self.update_stats()

    def quest_refuse_cop_info(self):
        self.player['respect'] = max(0, self.player['respect'] - 1)
        self.show_popup('Отказался, уважение -1!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_form_alliance(self):
        enemy = random.choice(self.enemy_districts)
        enemy['relations'] += 20
        self.player['respect'] = min(100, self.player['respect'] + 5)
        self.show_popup(f'Союз с {enemy["name"]} районом, уважение +5!')
        self.sounds['win'].play()
        self.update_stats()

    def quest_refuse_alliance(self):
        enemy = random.choice(self.enemy_districts)
        enemy['relations'] -= 10
        self.player['respect'] = max(0, self.player['respect'] - 2)
        self.show_popup(f'Отказался от союза с {enemy["name"]} районом, уважение -2!')
        self.sounds['lose'].play()
        self.update_stats()

    def quest_punish_thief(self):
        if self.player['boys'] > 0:
            self.player['boys'] -= 1
            self.player['fear'] = min(100, self.player['fear'] + 5)
            self.show_popup('Наказал вора, -1 пацан, страх +5!')
            self.sounds['fight'].play()
        else:
            self.show_popup('Пацанов нет, наказать некого!')
        self.update_stats()

    def quest_forgive_thief(self):
        self.player['respect'] = max(0, self.player['respect'] - 3)
        self.show_popup('Простил вора, уважение -3!')
        self.sounds['lose'].play()
        self.update_stats()

class BratvaApp(App):
    def build(self):
        return BratvaGame()

if __name__ == '__main__':
    BratvaApp().run()