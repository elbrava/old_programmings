import random
import sys
import threading
from string import Template
from kivy.core import window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
import datetime
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.picker import MDDatePicker
from kivymd.utils.asynckivy import sleep
import hashlib
import firebase_admin
from firebase_admin import credentials, db, auth
from kivy.storage.jsonstore import JsonStore

user = ""
trials = 0
correct_trials = 0
incorrect = 0
kv = Builder.load_file("sara_tutor.kv")

cred = credentials.Certificate(
    "firebase_sdk.json"
)
app = firebase_admin.initialize_app(cred, {
    "databaseURL": "https://sara-6bac6-default-rtdb.firebaseio.com/"
})

window.Window.size = (580, 700)

one = True
music1 = SoundLoader.load("bensound-clearday.mp3")
music2 = SoundLoader.load("bensound-funnysong.mp3")


def player_pre(*args):
    print("working")

    if one:
        play1()
    else:
        play2()


setting = JsonStore("settings.json")["settings"]
music1.volume = setting["sound"]["MUSIC"] / 100
music1.bind(on_stop=player_pre)
print(music1.volume)
setting = JsonStore("settings.json")["settings"]
music2.volume = setting["sound"]["MUSIC"] / 100
music2.bind(on_stop=player_pre)
print(music2.volume)


def online():
    import requests
    url = "http://www.kite.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
    except Exception:
        Offline_Popup().open()
        return False

    else:
        return True


def update():
    print("updatimg")
    list_user = []
    update_dict = {}
    store = JsonStore("users.json")
    try:
        s = store.store_get(store.store_keys()[0])
        print(s.store_keys)
        if len(s.store_keys()) < 2:
            raise ValueError
    except Exception as e:
        print(e)
    else:
        for key in s:
            if type(s[key]) == dict:
                list_user.append(key)
        for user in list_user:
            dict_user = s[user]
            update_dict.update({user: dict_user})
        print(update_dict)
        db.reference(s["SSD"]).update(update_dict)


def play1(*args):
    global one
    global music1, music2
    if one:
        if music1:
            music1.play()
            one = False


def play2(*args):
    global one
    global music2
    if not one:
        if music2:
            music2.play()
            one = True


class Button_Round(Button):
    def __init__(self, **kwargs):
        super(Button_Round, self).__init__(**kwargs)
        self.halign = "right"
        self.background_color = [0.4, 0.7, 1, 1]
        # print(self.ids.canvas)
        # self.optimize()

    def button_handle(self):
        global user
        print("called")
        print(self.text)
        user = self.text


class Button_Norm(Button):
    def __init__(self, **kwargs):
        super(Button_Norm, self).__init__(**kwargs)
        self.background_normal = ""

    def press(self):
        global user
        user = self.text


class Home(Screen):

    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

    def on_enter(self, *args):
        dicts = []
        no_user = False
        store = JsonStore("users.json")
        if store.keys():
            users_list = store.get(store.store_keys()[0])

            for l in users_list:
                if type(users_list[l]) == dict:
                    dicts.append(l)

        if len(dicts) == 0:
            no_user = True
        if no_user:
            self.ids.settings.disabled = True
            self.ids.settings.opacity = 0
            self.ids.add.disabled = True
            self.ids.add.opacity = 0

        Max_User().dismiss()
        Signup_Popup().dismiss()
        try:
            t1 = threading.Thread(target=update).start()
        except:
            pass


class User_Choose(Screen):
    def __init__(self, *args, **kwargs):
        super(User_Choose, self).__init__(**kwargs)
        store = JsonStore("users.json")
        if store.keys():
            users_list = store.get(store.store_keys()[0])
            print(users_list)

            """
            ADD
            SETTINGS
            NO USERS
            """

    def on_enter(self, *args):
        dicts = []
        store = JsonStore("users.json")
        if store.keys():
            users_list = store.get(store.store_keys()[0])
            c = Carousel()
            c.direction = "right"
            for l in users_list:
                if type(users_list[l]) == dict:
                    dicts.append(l)
                    b = Button_Round()
                    b.pos = (self.width / 2, 0)
                    b.background_color = (0, 0, 0, 0)
                    # set up circle color
                    b.font_size = dp(70)
                    b.font_name = "CuteAurora-PK3lZ.ttf"
                    b.color = users_list[l]["Color"]
                    cols = []
                    for i in range(3):
                        col = 1.0 - b.color[i]
                        cols.append(col)
                    cols.append(1)
                    print(cols)
                    b.background_color = cols
                    b.background_normal = ""
                    b.size_hint = (0.51, 0.1)
                    b.pos_hint = {"center_x": 0.63, "center_y": 0.5}
                    b.text = l
                    c.add_widget(b)
            self.add_widget(c)

        if len(dicts) == 0:
            Signup_Popup().open()


class Wrong_Credentials(Popup):
    def __init__(self, **kwargs):
        super(Wrong_Credentials, self).__init__(**kwargs)
        # t = threading.Thread(target=player_pre)
        # t.start()

    def back(self):
        Signup_Popup().open()


class Login_Screen(Screen):

    def __init__(self, **kwargs):
        super(Login_Screen, self).__init__(**kwargs)

        self.dict = {}
        self.email = self.ids.email.text
        self.passwrd = ''

    def on_enter(self, *args):
        self.ids.log_in.text = "LOG IN"

    def log_in(self):
        try:
            SSD = self.passwrd
            print(SSD)
            user = auth.get_user(SSD)
        except Exception as e:
            print(e)
            Wrong_Credentials().open()
        else:

            return SSD

    invalidates = []

    def email_validate(self, email):
        import re
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def validate(self):
        Signup_Screen.invalidates = []
        self.passwrd = hashlib.pbkdf2_hmac('sha256', self.ids.email.text.encode(), self.ids.password.text.encode(),
                                           iterations=7777).hex()
        self.email = self.ids.email.text
        try:
            if not self.email_validate(self.email):
                Signup_Screen.invalidates.append("email")
        except:
            pass
        if not Signup_Screen.invalidates:
            if online():
                ssd = str(self.log_in())
                if ssd is None:
                    self.ids.email.text = ''
                    self.ids.password.text = ''
                else:
                    try:
                        ref = db.reference(ssd)
                        self.dict = ref.get()
                        if self.dict is not None:
                            store = JsonStore("users.json")
                            store.clear()
                            store[self.email] = {"SSD": self.passwrd, **self.dict}
                            print(store.get(store.store_keys()[0]))
                            store2 = JsonStore("results.json")
                            for use_r in self.dict.keys():
                                store2[use_r] = {}

                            self.ids.log_in.text = "Successfully Logged In"
                    except Exception:
                        self.ids.email.text = ''
                        self.ids.password.text = ''
                        Wrong_Credentials().open()
        else:
            Invalids(Signup_Screen.invalidates).open()

        # email validation
        # internet error
        # fireBase

    def save(self):
        """"
        saave user and database

        """
        pass


"""
add button
setting button
if no users add user
setting
"""


class Introduction_Screen(Screen):
    def __init__(self, *args, **kwargs):
        super(Introduction_Screen, self).__init__(**kwargs)
        self.toggle = True
        self.age_limit = 1
        self.age = 0

        store = JsonStore("users.json")
        try:
            store_contents = store.get(store.store_keys()[0])
            users_list = []
            print(store_contents)
            for u in store_contents:
                print(u)
                if type(store_contents[u]) == dict:
                    users_list.append(u)

            if Introduction_Screen.user == "":
                pass
            if store.keys():
                try:
                    self.age_limit = store_contents[Introduction_Screen.user]["Age"]

                    self.ids.user.text = f" Hello {Introduction_Screen.user}"
                    self.ids.age.text = str(self.age)
                except KeyError:
                    pass
        except:
            pass

    def on_enter(self, *args):
        store = JsonStore("users.json")
        s = store.store_get(store.store_keys()[0])
        l = s[user]
        Calculation_Screen.level = l["Level"]
        dob = l["Date_of_birth"].split("-")
        age = self.age_calculate(int(dob[0]), int(dob[1]), int(dob[2]))
        print(age)
        self.age_limit = int(age)
        store_contents = store.get(store.store_keys()[0])

        if store.keys():
            try:
                self.ids.user.text = f" Hello {user}"
                self.ids.age.text = str(self.age)
            except KeyError:
                pass
        self.age = 0
        if self.age <= self.age_limit:
            Clock.schedule_interval(self.increase, .14)

    def increase(self, *args):
        validate = False
        if self.age <= self.age_limit - 1:
            self.age += 1
            self.ids.age.text = str(self.age)
            validate = False
        else:
            self.ids.age.text = "Ready"

    def age_calculate(self, year, month, date):
        print(year, month, date)
        date_today = datetime.date.today()
        date_of_birth = datetime.date(year, month, date)
        days = date_today - date_of_birth
        days = f"{days / 365}".split(",")
        days = days[0]
        years = days.split(" ")[0]
        return years


class Calculation_Screen(Screen, Widget):
    calculation = ""
    calculation_list = []
    try:
        store = JsonStore("users.json")
        s = store[store.store_keys()[0]]
        l = s[user]
        dob = l["Date_of_birth"].split("-")
        level = l["Level"]
    except:
        level = 1

    def __init__(self, **kwargs):

        super(Calculation_Screen, self).__init__(**kwargs)
        self.answer_validate = True
        self.user_input = ''
        self.user_answer = 0
        self.user_remainder = 0
        self.num1 = 0
        self.num2 = 0
        self.addition = False
        self.subtraction = False
        self.multiplication = False
        self.division = False
        self.answer = 0
        self.remainder = 70
        self.missed = []
        # default
        Clock.schedule_once(self.operate, 3)

        # main object
        # self.add_widget(self.main)
        # handles calculation and levels

    def on_enter(self, *args):

        store = JsonStore("users.json")
        s = store.store_get(store.store_keys()[0])
        l = s[user]
        Calculation_Screen.level = l["Level"]
        dob = l["Date_of_birth"].split("-")
        age = self.age_calculate(int(dob[0]), int(dob[1]), int(dob[2]))
        print(age)
        age = 17 - int(age)
        print(age)
        print("Level", Calculation_Screen.level)
        Calculation_Screen.level = int(Calculation_Screen.level - age)

        Calculation_Screen.level = int(Calculation_Screen.level / 2.1)
        if Calculation_Screen.level <= 1:
            Calculation_Screen.level = 1
        print("Level", Calculation_Screen.level)

    def operate(self, *args):
        self.addition = False
        self.subtraction = False
        self.multiplication = False
        self.division = False
        rand = random.randint(1, 4)
        self.answer_pre()
        print("operate")
        if rand == 1:
            self.addition = True
        elif rand == 2:
            self.subtraction = True
        elif rand == 3:
            self.multiplication = True
        elif rand == 4:
            self.division = True

        self.ids.user_input.text = ""
        if self.addition:
            self.num1 = random.randint(
                1 * Calculation_Screen.level, 7 * Calculation_Screen.level)
            self.num2 = random.randint(
                1 * Calculation_Screen.level, 7 * Calculation_Screen.level)
            self.answer = self.num1 + self.num2
            self.remainder = 0
            print("Add:", self.num1, "+", self.num2)
            self.label_text(f"Add: {self.num1} + {self.num2}")
        if self.subtraction:
            self.num1 = random.randint(
                3 * Calculation_Screen.level, 7 * Calculation_Screen.level)
            self.num2 = random.randint(
                0 * Calculation_Screen.level, 3 * Calculation_Screen.level)
            self.answer = self.num1 - self.num2
            self.remainder = 0
            print("Subtract:", self.num1, "-", self.num2)
            self.label_text(f"Subtract: {self.num1} - {self.num2}")
        if self.multiplication:
            self.num1 = random.randint(
                0 + Calculation_Screen.level, 7 * Calculation_Screen.level)
            self.num2 = random.randint(
                0 + Calculation_Screen.level, 7 + Calculation_Screen.level)
            self.answer = self.num1 * self.num2
            self.remainder = 0
            print("Multiply:", self.num1, "*", self.num2)
            self.label_text(f"Multiply:{self.num1} * {self.num2}")
        if self.division and Calculation_Screen.level <= 30:
            self.answer = 0
            while not (int(self.remainder) == 0 and int(self.answer) >> 0):
                self.num1 = random.randint(
                    4 + Calculation_Screen.level, 7 + Calculation_Screen.level)
                self.num2 = random.randint(
                    1 + Calculation_Screen.level, 4 + Calculation_Screen.level)
                self.answer = self.num1 // self.num2
                self.remainder = self.num1 % self.num2
                print("Divide:", self.num1, "/", self.num2)
                print(self.answer, self.remainder)
            self.label_text(f"Divide: {self.num1} / {self.num2}")
            # print("Find only the divisor and ignore the remainder")
        elif self.division and not Calculation_Screen.level >> 30:
            self.num1 = random.randint(
                4 * Calculation_Screen.level, 7 * Calculation_Screen.level)
            self.num2 = random.randint(
                1 + Calculation_Screen.level, 4 + Calculation_Screen.level)
            self.answer = self.num1 // self.num2
            self.remainder = self.num1 % self.num2
            print("Divide:", self.num1, "/", self.num2)
            print(self.answer, self.remainder)
            self.label_text(f"Divide: {self.num1} / {self.num2}")
        self.calculation = self.ids.label_calculate.text
        if self.calculation_list.__contains__(self.calculation):
            self.operate()
        else:
            self.calculation_list.append(self.calculation)
            self.ids.label_calculate.text += "\nAnswer:"

    def label_text(self, msg=""):
        print(msg)
        self.ids['label_calculate'].text = f"{msg}"

    def button_touch(self, widget):
        if widget.text == "Clear":
            try:
                user_input_list = list(self.ids.user_input.text)
                user_input_list.pop()
                self.ids.user_input.text = "".join(user_input_list)

            except Exception:
                pass
        elif widget.text == "Enter":
            pass
        else:
            self.user_input = ""
            print(self.ids.user_input.text)
            print(widget.text)
            print(self.user_input)
            self.user_input += widget.text
            self.ids.user_input.text += self.user_input

    def answer_pre(self):
        self.label_text()
        self.answer_validate = True
        self.ids.enter_button.bind(
            on_press=self.answer_convert
        )
        self.ids.user_input.bind(
            on_text_validate=self.answer_convert)

    def age_calculate(self, year, month, date):
        print(year, month, date)
        date_today = datetime.date.today()
        date_of_birth = datetime.date(year, month, date)
        days = date_today - date_of_birth
        days = f"{days / 365}".split(",")
        days = days[0]
        years = days.split(" ")[0]
        return years

    def answer_convert(self, *args):
        answer = self.ids.user_input.text
        answer1 = answer
        if self.answer_validate:
            try:
                if len(answer1) == 0:

                    sleep(3)
                    raise AssertionError
                else:
                    int(answer1)

                print(str(self.user_answer))
            except ValueError:
                Fail_Popup_INVALID_INPUT().open()
                self.ids.user_input.text = ""
            except AssertionError:
                # DUMMY ERROR
                Fail_Popup_NO_INPUT().open()

            else:

                self.user_answer = answer1
                self.ids.label_calculate.text += self.user_answer
                self.ids.user_input.text = ""
                self.answer_post()

    def answer_post(self):
        if self.remainder == 0:
            self.user_remainder = 0
            self.main()
        else:
            self.remainder_pre()

    def remainder_pre(self):
        self.ids.label_calculate.text += "\nRemainder:"
        self.answer_validate = False
        self.ids.enter_button.bind(
            on_press=self.remainder_convert
        )
        self.ids.user_input.bind(
            on_text_validate=self.remainder_convert)

    def remainder_convert(self, *args):
        pass

        print("error")
        remainder = self.ids.user_input.text
        remainder1 = remainder
        if not self.answer_validate:
            try:
                if len(remainder1) == 0:

                    sleep(3)
                    raise AssertionError
                else:
                    int(remainder1)
            except ValueError:
                Fail_Popup_INVALID_INPUT().open()
                self.ids.user_input.text = ""
            except AssertionError:
                # DUMMY ERROR
                Fail_Popup_NO_INPUT().open()

            else:
                self.user_remainder = remainder1
                self.ids.label_calculate.text += self.user_remainder
                self.ids.user_input.text = ""
                self.remainder_post()

    def remainder_post(self):
        self.main()

    def main(self):

        global trials, correct_trials, incorrect
        # reset value
        trials += 1
        print(f"REMAINDER:{self.user_remainder},Answer:{self.user_answer}")
        print("Trials:", trials, " Correct trials:", correct_trials)
        if incorrect >= 3:

            print("The answer is ", self.answer)
            print("The remainder is", self.remainder)
            if self.remainder != 0:
                self.label_text(f"""
                   The answer is  {self.answer}
                   The remainder is  {self.remainder}
                   """)
            else:
                self.label_text(f"The answer is  {self.answer}")
            incorrect = 0
            store = JsonStore("users.json")
            email = store.store_keys()[0]
            s = store.store_get(store.store_keys()[0])
            l = s[user]
            l["Missed_Calculation"].append(self.calculation)
            store[email] = s
            Clock.schedule_once(self.operate, 3)
        else:
            if self.answer == int(self.user_answer) and self.remainder == int(self.user_remainder):
                print("Correct Answer")
                correct_trials += 1
                print("Correct trials:", correct_trials)
                Correct_Popup().open()

                Clock.schedule_once(self.operate, 3)

            elif self.remainder != int(self.user_remainder) and self.answer == int(self.user_answer):
                Fail_Popup_WRONG_REM().open()
                print("Your remainder is incorrect")
                print("Try again")
                incorrect += 1
                label_list = list(self.ids.label_calculate.text)
                print("Incorrect", incorrect)
                self.ids.label_calculate.text = f"""
                {self.calculation_list[-1]}
                Answer:{self.user_answer}
                Remainder:
                """
                self.remainder_pre()
                store = JsonStore("users.json")
                # continue
                if not self.missed.__contains__(self.calculation):
                    self.missed.append(self.calculation)
            else:
                self.answer_pre()
                Fail_Popup_WRONG_ANSWER().open()
                print("Your Answer is incorrect")
                print("Try again")
                incorrect += 1
                self.ids.label_calculate.text = f"{self.calculation_list[-1]}\nAnswer:"
                print("Incorrect", incorrect)
                # continue
                if not self.missed.__contains__(self.calculation):
                    self.missed.append(self.calculation)
        if correct_trials >= round(7 + Calculation_Screen.level / 10):
            print("correct trials:", correct_trials)
            print('trials:', trials)
            percentage = (correct_trials / trials) * 100
            self.record(percentage)
            print("You have", percentage, "percent")
            print("Thank you for participating")
            correct_trials = 0
            trials = 0

    def record(self, records):
        Calculation_Screen.levelling(int(records))
        store = JsonStore("results.json")
        date_today = datetime.datetime.today()
        date_today = str(date_today).split(".")[0]
        s = store["users"]
        s[user][date_today] = records
        store.clear()
        store["users"] = s

        Results_Popup(int(records), self.missed).open()

        # if online():
        #   pass
        # Sara_Tutor_App().async_run(update())

    @classmethod
    def levelling(cls, percen_tage):
        store = JsonStore("users.json")
        s = store.store_get(store.store_keys()[0])
        l = s[user]
        level = l["Level"]
        le_v_el = level
        if percen_tage >= 84:
            le_v_el += 1
            print(f"nice work,{le_v_el}")
        elif percen_tage <= 35:
            le_v_el -= 1
            if le_v_el <= 1:
                le_v_el = 1
            print(f"try harder {le_v_el}")
        else:
            print("level_____up")
        store = JsonStore("users.json")
        email = store.store_keys()[0]
        s = store.store_get(email)
        s[user]["Level"] = le_v_el
        store.clear()
        store[email] = s

    def quit(self, dt):
        pass


# done

class Screen_Manager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(Screen_Manager, self).__init__(**kwargs)
        self.add_widget(Home(name="home"))
        self.add_widget(User_Choose(name="user_choose"))
        self.add_widget(Introduction_Screen(name="introduction"))
        self.add_widget(Calculation_Screen(name="calculation"))
        self.add_widget(Login_Screen(name="log_in"))
        self.add_widget(Signup_Screen(name="sign_up"))
        self.add_widget(Signup_Screen_user(name="sign_up_user"))
        self.add_widget(Settings_Screen(name="settings"))
        self.add_widget(Admin_Modify(name="admin"))
        self.add_widget(Sound_Screen(name="sound"))
        self.add_widget(User_Modify(name="user_modify"))
        self.add_widget(User_Modify_Pre(name="user_modify_pre"))
        print(self.screens)
        self.screen_list = ["user_choose", "introduction", "calculation", "log_in", "sign_up", "sign_up_user"]

    def user_choose(self, *args):
        self.current = 'user_choose'

    def introduction(self, *args):
        self.current = 'introduction'
        print("intro")

    def calculation(self, *args):
        self.current = 'calculation'

    def log_in(self, *args):
        self.current = 'log_in'

    def sign_up(self, *args):
        self.current = 'sign_up'

    def sign_up_user(self, *args):
        self.current = 'sign_up_user'

    def user_modify_pre(self):
        self.current = "user_modify_pre"

    def user_modify(self):
        self.current = "user_modify"

    def admin_modify(self):
        self.current = "admin"

    def sound(self):
        self.current = "sound"

    def settings(self):
        self.current = "settings"


class Email_Sent(Popup):
    def __init__(self, msg, **kwargs):
        super(Email_Sent, self).__init__(**kwargs)
        self.title = "EMAIL"
        self.title_size = dp(49.0)
        b = Button()
        b.text = msg
        self.add_widget(b)
        Clock.schedule_once(self.dismiss, 2)

class Signup_Screen(Screen):
    invalidates = []

    def __init__(self, *args, **kwargs):
        super(Signup_Screen, self).__init__(**kwargs)
        self.link_verification = ''
        self.email = ""
        self.password = ""
        self.password1 = ""
        self.dict = {}

    def user_add(self):
        if online():
            try:
                auth.create_user(uid=self.password, email=self.email, password=self.password)
                self.link_verification = auth.generate_email_verification_link(self.email)
            except Exception as e:
                print(e)
                User_Exists().open()
            else:
                ref = db.reference('/')
                ref.set(self.password)
                self.ids.sign_up.text = "Successfully Added"
                t = threading.Thread(target=self.email_send)
                t.start()
                Email_Sent(f"Kindly Check\n {self.email} \nTo Activate \nYour Account").open()
                return self.password

    def email_validate(self, email):
        import re
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def validate(self):
        Signup_Screen.invalidates = []
        self.password = self.ids.password.text
        self.password1 = self.ids.password_confirm.text
        if self.password == "" or self.password1 == "":
            if not Signup_Screen.invalidates.__contains__("password"):
                Signup_Screen.invalidates.append("password")
        self.email = self.ids.email.text
        self.password = hashlib.pbkdf2_hmac(
            'sha256', self.email.encode(), self.password.encode(), 7777).hex()
        self.password1 = hashlib.pbkdf2_hmac(
            'sha256', self.email.encode(), self.password1.encode(), 7777).hex()
        try:
            if not self.email_validate(self.email):
                Signup_Screen.invalidates.append("email")
            if not self.password == self.password1:
                if not Signup_Screen.invalidates.__contains__("password"):
                    Signup_Screen.invalidates.append("password")
            print(Signup_Screen.invalidates)
        except:
            pass
        if not Signup_Screen.invalidates:
            ssd = str(self.user_add())
            if ssd is None:
                self.ids.email.text = ""
                self.ids.password.text = ""
            else:
                store = JsonStore("users.json")
                store.clear()
                d = {"SSD": self.password, **self.dict}
                store[self.email] = d
                print(store.get(store.store_keys()[0]))

        else:
            Invalids(Signup_Screen.invalidates).open()

        # email validation
        # internet error
        # fireBase

    def save(self):
        """"
        saave user and database

        """
        pass

    def email_send(self):
        import smtplib
        from email.message import EmailMessage
        if online():
            psrd = "xvbiephtkeqwynhb"
            sender = "bravo.ale.mando@gmail.com"
            recipient = self.email
            subject = "ACCOUNT ACTIVATION"
            message = "ACTIVATE YOUR ACCOUNT"
            msg = EmailMessage()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.set_content(message)
            t = Template("""
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sara</title>
</head>

<body>
    <div>
        Thank you for creating<br /> An account with Sara <br /> Click button below to activate
    </div>
    <div class="button">
        <a href=$link>
            <button><h1>ACTIVATE</h1></button>
        </a>
    </div>

    <style>
        body {
            background: rgb(112, 41, 99);
        }
        
        div {
            color: rgb(143, 214, 156);
            text-align: center;
            font-size: 300%;
        }
        
        a {
            margin: 0 auto;
        }
        
        button {
            background: rgb(143, 214, 156);
            color: rgb(112, 41, 99);
            border: 4px solid white;
            border-radius: 49px;
            margin: 0 auto;
        }
    </style>
</body>

</html>

    """)

            msg.add_alternative(t.substitute({"link": f"{self.link_verification}"}), subtype="html")
            # issue detected pass *args
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(sender, psrd)
                smtp.send_message(msg)
            Email_Sent(f"Email has been sent to {self.email}").open()


class Account_Exists(Popup):
    def __init__(self, **kwargs):
        super(Account_Exists, self).__init__(**kwargs)
        Clock.schedule_once(self.dismiss, 2)


class Signup_Screen_user(Screen):
    invalidates = []

    def __init__(self, **kwargs):
        super(Signup_Screen_user, self).__init__(**kwargs)
        self.age = 1
        self.date_dialog = MDDatePicker()
        self.first_name = ""
        self.second_name = ""
        self.date_of_birth = ""
        self.colour = [random.uniform(0.0, 1.0) for i in range(3)]
        self.colour.append(1)
        self.level = 1
        self.missed_calculations = []
        """
        FAILED CALCULATION

        """
        self.dict = {
            "Second_name": self.second_name,
            "Color": self.colour,
            "Date_of_birth": self.date_of_birth,
            "Level": self.level,
            "Missed_Calculations": self.missed_calculations,
        }
        self.CONFIRM_with_list()

    def validate(self):
        print("Validate")
        Signup_Screen_user.invalidates = []
        self.first_name = self.ids.first_name.text
        self.second_name = self.ids.second_name.text
        self.date_of_birth = self.ids.date_of_birth.text
        try:
            if self.first_name == "":
                Signup_Screen_user.invalidates.append("first name")
            if self.second_name == "":
                Signup_Screen_user.invalidates.append("second name")
            if self.date_of_birth == 'Date Picker':
                Signup_Screen_user.invalidates.append("date")
            date = self.ids.date_of_birth.text
            date = date.split('-')
            date = list(date)
            print(date)

            try:
                self.age = int(self.age_calculate(year=int(date[0]), month=int(date[1]), date=int(date[2])))
                print(self.age)
                if self.age <= 4:
                    raise ValueError
            except ValueError:
                if not Signup_Screen_user.invalidates.__contains__("date"):
                    Signup_Screen_user.invalidates.append("date")
            else:
                if Signup_Screen_user.invalidates.__contains__("date"):
                    Signup_Screen_user.invalidates.remove("date")


        except:
            pass

        if not Signup_Screen_user.invalidates:
            if self.CONFIRM_with_list() and not self.exists():
                self.dict = {
                    "Second_name": self.second_name,
                    "Color": self.colour,
                    "Date_of_birth": self.date_of_birth,
                    "Level": self.level,
                    "Missed_Calculation": ["dummy value"],
                }
                store = JsonStore("users.json")
                store2 = JsonStore("results.json")
                original = store.get(store.store_keys()[0])
                original[self.first_name] = self.dict
                store2["user"][self.first_name] = {}
                store[store.store_keys()[0]] = original
                if online():
                    ref = db.reference(original["SSD"])
                    ref.child(self.first_name).set(self.dict)

                    self.ids.sign_up_users.text = "Successfully Added"

            elif self.exists():
                Account_Exists().open()
        else:
            Invalids(Signup_Screen_user.invalidates).open()

    def exists(self):
        user_list = []
        store = JsonStore("users.json")
        users = store.get(store.store_keys()[0])
        for u in users:
            if type(users[u]) == dict:
                user_list.append(u)
        if user_list.__contains__(self.first_name):
            return True

    def CONFIRM_with_list(self):
        try:
            print("CALLED")
            store = JsonStore("users.json")
            users = []

            users_list = store.get(store.store_keys()[0])
            print(users_list)
            for l in users_list:
                if type(users_list[l]) == dict:
                    users.append(l)
            if len(users) >= 4:
                Max_User().open()
                return False
            else:
                if users.__contains__(self.first_name):
                    User_Exists().open()
                    return False
                else:
                    return True
        except:
            pass

    def date_picker(self):

        try:
            date = datetime.date(",".join(self.ids.date_of_birth.text.split('-')))
            print(date)
        except:
            try:
                today = datetime.datetime.today()
                self.date_dialog = MDDatePicker(
                    min_year=today.year - 16,
                    max_year=today.year - 4
                )
            except RecursionError:
                self.date_dialog.dismiss()

        else:
            date = self.ids.date_of_birth.text.split("-")
            try:
                today = datetime.datetime.today()
                self.date_dialog = MDDatePicker(
                    min_year=today.year - 16,
                    max_year=today.year - 4,
                    year=date[0],
                    month=date[1],
                    day=date[2])
                self.date_dialog.open()
            except RecursionError:
                self.date_dialog.dismiss()
            self.date_dialog.bind(on_save=self.on_save)
        finally:
            self.date_dialog.open()
            self.date_dialog.bind(on_save=self.on_save)

    def age_calculate(self, year, month, date):
        print(year, month, date)
        date_today = datetime.date.today()
        date_of_birth = datetime.date(year, month, date)
        days = date_today - date_of_birth
        days = f"{days / 365}".split(",")
        days = days[0]
        years = days.split(" ")[0]
        return years

    def on_save(self, instance, value, date_range):
        date = self.ids.date_of_birth.text = str(value)
        date = date.split('-')
        date = list(date)
        print(date)

        try:
            self.age = int(self.age_calculate(year=int(date[0]), month=int(date[1]), date=int(date[2])))
            print(self.age)
            if self.age <= 4:
                raise ValueError
        except ValueError:
            if not Signup_Screen_user.invalidates.__contains__("date"):
                Signup_Screen_user.invalidates.append("date")
        else:
            if Signup_Screen_user.invalidates.__contains__("date"):
                Signup_Screen_user.invalidates.remove("date")


# final

class Signup_Popup(Popup):
    def __init__(self, **kwargs):
        super(Signup_Popup, self).__init__(**kwargs)
        #t = threading.Thread(target=player_pre)
        #t.start()


class Correct_Popup(Popup):
    def __init__(self, **kwargs):
        super(Correct_Popup, self).__init__(**kwargs)
        self.title = "CORRECT ANSWER"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = 0.7, 0.7
        b = Button()
        b.text = "YOUR ANSWER \n IS CORRECT"
        self.add_widget(b)

        self.sound = SoundLoader.load(

            "zapsplat_multimedia_alert_ping_chime_correct_answer_check_positive_007_70196.mp3")
        store = JsonStore("settings.json")
        sfx = store["settings"]["sound"]["SFX"]
        self.sound.volume = sfx / 100
        # self.sound.bind(on_stop=player_pre)
        t = threading.Thread(target=self.sound.play)
        t.start()
        Clock.schedule_once(self.dismiss, 2)


class Quit_Popup(Popup):
    def __init__(self, **kwargs):
        super(Quit_Popup, self).__init__(**kwargs)
        #t = threading.Thread(target=player_pre)
        #t.start()

    def quit(self):
        sys.exit()


class Results_Popup(Popup):
    def __init__(self, per_cen_tage, missed_calculations, **kwargs):
        self.title = "RESULTS"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = (0.7, 0.7)
        super(Results_Popup, self).__init__(**kwargs)
        self.percentage = per_cen_tage
        store = JsonStore("users.json")
        self.email = store.store_keys()[0]
        email = self.email.split("@")[0]
        store2 = JsonStore("results.json")
        s = store2["users"][user]
        s = dict(s)
        self.labels = s.keys()
        self.data = [s[key] for key in self.labels]
        self.message = f"You have \nscored  {self.percentage}\nThis results have\n been sent to \n{email}"
        self.missed = missed_calculations
        self.time_date = datetime.datetime.today()
        self.time_date = str(self.time_date).split(".")[0]
        b = Button()
        b.text = self.message
        b.halign = "center"
        self.add_widget(b)
        t = threading.Thread(target=self.email_send)
        t.start()
        #t1 = threading.Thread(target=player_pre)
        #t1.start()
        if online():
            t1 = threading.Thread(target=update).start()

    def email_send(self):
        import smtplib
        message = ""
        from email.message import EmailMessage
        if len(self.missed) == 0:
            message = f"{user} has passed everything"
        else:
            m = "\n    ".join(self.missed)
            message = f"{user} failed;<br>{m}"

        if online():
            psrd = "xvbiephtkeqwynhb"
            sender = "bravo.ale.mando@gmail.com"
            recipient = self.email
            subject = f"{user}"
            msg = EmailMessage()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.set_content("Results")
            if len(self.labels) >= 4:
                t = Template("""<html lang="en">
    
    <head></head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Chart</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.5.1/chart.min.js"></script>
    
    </head>
    
    
    <body>
    
        <div class="container">
            <div>
                <h1>
                    Thank you for using SARA
                    <br> $user has scored $percentage at $time_date_today
                    <br> $message
                </h1>
            </div>
            <canvas class="chart"></canvas>
        </div>
    
        <style>
            canvas {
                border-radius: 49px;
                color: white;
            }
            
            body {
                background-color: rgba(143, 214, 156, 1);
            }
            
            h1 {
                color: rgba(143, 214, 156, 1);
            }
            
            div {
                background: rgba(112, 41, 99, 1);
                width: 79%;
                margin: 0 auto;
                border-radius: 49px;
                text-align: center;
            }
        </style>
        <script>
            var chart_canvas = document.getElementsByClassName("chart");
            const data = {
                labels: $date_time,
                datasets: [{
                    label: 'SCORE',
                    data: $data,
                    fill: false,
                    borderColor: 'rgb(143, 214, 156)',
                    tension: 0,
    
                }]
            };
            Chart.defaults.color = "rgb(255,255,255)"
    
            var config = {
                type: 'line',
                data: data,
                responsive: true,
                scaleFontColor: "#FFFFFF",
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: '$user results',
                            font: {
                                size: 27,
                                weight: "bold"
    
                            }
                        },
                        tooltip: {
                            enabled: true,
                            backgroundColor: "rgb(143, 214, 156)"
                        },
    
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Score",
                                font: {
                                    size: 21,
                                    weight: "bold"
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: "Date Time",
                                font: {
                                    size: 21,
                                    weight: "bold",
    
                                },
    
                            }
    
                        }
                    }
    
                },
    
            }
    
            var chart = new Chart(chart_canvas, config);
        </script>
    </body>
    
    </html>
    """)
                msg.add_alternative(t.substitute({"user": user,
                                                  "percentage": self.percentage,
                                                  "message": message,
                                                  "time_date_today": self.time_date,
                                                  "data": self.data,
                                                  "date_time": self.labels,
                                                  }), subtype="html")

            else:
                t = Template("""<html lang="en">

                   <head></head>
                   <meta charset="UTF-8" />
                   <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                   <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                   <title>Chart</title>
                   </head>
                   <body>
                       <div class="container">
                           <div>
                               <h1>
                                   Thank you for using SARA
                                   <br> $user has scored $percentage at $time_date_today
                                   <br> $message
                               </h1>
                           </div>
                       </div>
                       <style>
                           body {
                               background-color: rgba(143, 214, 156, 1);
                           }

                           h1 {
                               color: rgba(143, 214, 156, 1);
                           }

                           div {
                               background: rgba(112, 41, 99, 1);
                               width: 79%;
                               margin: 0 auto;
                               border-radius: 49px;
                               text-align: center;
                           }
                       </style>

                   </body>

                   </html>
                   """)

                msg.add_alternative(t.substitute({"user": user,
                                                  "percentage": self.percentage,
                                                  "message": message,
                                                  "time_date_today": self.time_date,
                                                  }), subtype="html")

            # issue detected pass *args
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(sender, psrd)
                smtp.send_message(msg)
            self.quit()

    def quit(self, *args):
        print("WERTYUIOP")
        Quit_Popup().open()
        self.dismiss()


class Fail_Popup_NO_INPUT(Popup):
    def __init__(self, **kwargs):
        super(Fail_Popup_NO_INPUT, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = 0.7, 0.7
        b = Button()

        background_color: (1, 0.7, 0.7, 0)

        self.message = "PLEASE TYPE\n A NUMBER   "

        b.text = self.message
        self.add_widget(b)
        print("initialized")
        Clock.schedule_once(self.dismiss, 2.1)
        #t = threading.Thread(target=player_pre)
        #t.start()


class Fail_Popup_WRONG_ANSWER(Popup):
    def __init__(self, **kwargs):
        super(Fail_Popup_WRONG_ANSWER, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = 0.7, 0.7
        b = Button()
        background_color: (1, 0.7, 0.7, 0)
        self.message = "INCORRECT  \n ANSWER \n TRY AGAIN"
        b.text = self.message
        self.add_widget(b)
        print("initialized")
        self.sound = SoundLoader.load(

            "zapsplat_multimedia_game_show_buzzer_001_27373.mp3")
        store = JsonStore("settings.json")
        sfx = store["settings"]["sound"]["SFX"]
        self.sound.volume = sfx / 100
        # self.sound.bind(on_stop=player_pre)
        t = threading.Thread(target=self.sound.play)
        t.start()
        Clock.schedule_once(self.dismiss, 2.1)


class Fail_Popup_WRONG_REM(Popup):
    def __init__(self, **kwargs):
        super(Fail_Popup_WRONG_REM, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = 0.7, 0.7
        b = Button()
        background_color: (1, 0.7, 0.7, 0)
        self.message = "INCORRECT \n REMAINDER \n TRY AGAIN "
        b.text = self.message
        self.add_widget(b)
        print("initialized")
        Clock.schedule_once(self.dismiss, 2.1)
        self.sound = SoundLoader.load(

            "zapsplat_multimedia_alert_ping_chime_correct_answer_check_positive_007_70196.mp3")
        store = JsonStore("settings.json")
        sfx = store["settings"]["sound"]["SFX"]
        self.sound.volume = sfx / 100
        # self.sound.bind(on_stop=player_pre)
        t = threading.Thread(target=self.sound.play)
        t.start()


class Fail_Popup_INVALID_INPUT(Popup):
    def __init__(self, **kwargs):
        super(Fail_Popup_INVALID_INPUT, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = 0.7, 0.7
        b = Button()

        background_color: (1, 0.7, 0.7, 0)
        """
        invalid input
        no input
        wrong answer
        error in email
        """
        self.message = "INVALID INPUT \n  TRY AGAIN"
        b.text = self.message
        self.add_widget(b)
        print("initialized")
        Clock.schedule_once(self.dismiss, 2.1)


class Fail_Popup_EMAIL_ERROR(Popup):
    def __init__(self, **kwargs):
        super(Fail_Popup_EMAIL_ERROR, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.title_size = dp(49.0)
        self.size_hint = 0.7, 0.7
        b = Button()

        background_color: (1, 0.7, 0.7, 0)
        """
        invalid input
        no input
        wrong answer
        error in email
        """

        self.message = """

                SOMETHING  WRONG HAPPENED 
                IN SENDING THE EMAIL

                TRY AGAIN
                    Try connecting 
                    to the internet

                  """
        b.text = self.message
        self.add_widget(b)
        print("initialized")
        Clock.schedule_once(self.dismiss, 2.1)
        t = threading.Thread(target=player_pre)
        t.start()


class Invalids(Popup):
    def __init__(self, invalids, **kwargs):
        super(Invalids, self).__init__(**kwargs)
        self.title = "INVALID"
        self.title_size = dp(49.0)
        self.size_hint = (0.7, 0.7)
        b = Button()
        b.text = "You have invalid:\n"
        self.invalid_list = []
        self.invalid_list = invalids
        if len(self.invalid_list) >= 1:
            b.text += "\n".join(self.invalid_list)
        elif len(self.invalid_list) == 1:
            b.text += self.invalid_list[-1]
        self.add_widget(b)
        Clock.schedule_once(self.dismiss, 2)
        #t = threading.Thread(target=player_pre)
        #t.start()


class User_Exists(Popup):
    def __init__(self, **kwargs):
        super(User_Exists, self).__init__(**kwargs)
        Clock.schedule_once(self.dismiss, 3)
        #t = threading.Thread(target=player_pre)
        #t.start()


class Max_User(Popup):
    def __init__(self, **kwargs):
        super(Max_User, self).__init__(**kwargs)
        #t = threading.Thread(target=player_pre)
        #t.start()


class Offline_Popup(Popup):
    def __init__(self, **kwargs):
        super(Offline_Popup, self).__init__(**kwargs)
        self.size_hint = .7, .7
        self.auto_dismiss = False
        self.title = "INTERNET"
        self.title_size = dp(49.0)
        b = Button(text="Your are offline \n Kindly check your \n internet connection ")
        self.add_widget(b)
        t = threading.Thread(target=self.online_pre)
        t.start()
        #t = threading.Thread(target=player_pre)
        #t.start()

    def online_pre(self):
        Clock.schedule_interval(self.online_main, 3)

    def online_main(self, dt):
        import requests
        print("online")

        def online():
            url = "http://www.kite.com"
            timeout = 5
            try:
                request = requests.get(url, timeout=timeout)
            except (requests.ConnectionError, requests.Timeout) as exception:
                return False
            else:
                return True

        while not online():
            pass
        else:
            self.dismiss()


class Settings_Screen(Screen):
    pass


class Sound_Screen(Screen):
    def on_enter(self):
        store = JsonStore("settings.json")
        settings = store["settings"]
        self.ids.sfx.value = settings["sound"]["SFX"]
        self.ids.music.value = settings["sound"]["MUSIC"]

    def save(self):
        sfx = self.ids.sfx.value
        music = self.ids.music.value
        store = JsonStore("settings.json")
        settings = store["settings"]
        settings["sound"]["SFX"] = sfx
        settings["sound"]["MUSIC"] = music
        store.clear()
        store["settings"] = settings


class User_Modify_Pre(Screen):
    def __init__(self, **kwargs):
        super(User_Modify_Pre, self).__init__(**kwargs)

    def on_enter(self, *args):
        dicts = []
        store = JsonStore("users.json")
        print('hjkl;')
        if store.keys():
            users_list = store.get(store.store_keys()[0])
            c = BoxLayout()
            c.orientation = "vertical"
            print(users_list)
            for l in users_list:
                if type(users_list[l]) == dict:
                    dicts.append(l)
                    but_ton = Button_Norm()
                    print(but_ton)
                    but_ton.font_size = dp(70)
                    but_ton.color = users_list[l]["Color"]
                    cols = []
                    for i in range(3):
                        col = 1.0 - but_ton.color[i]
                        cols.append(col)
                    cols.append(1)
                    print(cols)
                    but_ton.background_color = cols
                    but_ton.text = l

                    c.add_widget(but_ton)
            self.add_widget(c)
            print("working")
        if len(dicts) == 0:
            Signup_Popup().open()


class User_Modify(Screen):
    def __init__(self, **kwargs):
        super(User_Modify, self).__init__(**kwargs)
        self.first_name = ""
        self.second_name = ""
        self.date_of_birth = ""
        self.date_dialog = MDDatePicker()
        self.color = []
        self.dict = {}
        self.age = 0

    invalidates = []

    def on_enter(self, *args):
        print(user, "GHJKL:"
                    "")
        store = JsonStore("users.json")
        user_dict = store[store.store_keys()[0]]
        print(user_dict[user])
        self.ids.first_name.text = user
        self.ids.second_name.text = user_dict[user]["Second_name"]
        self.ids.date_of_birth.text = user_dict[user]["Date_of_birth"]
        color = user_dict[user]["Color"]
        con_color = [1.0 - c for c in color]
        con_color.pop()
        con_color.append(1.0)
        self.ids.color.background_normal = ""
        self.ids.color.background_color = con_color
        self.ids.color.color = color

    def validate(self):
        print("Validate")
        Signup_Screen_user.invalidates = []
        self.first_name = self.ids.first_name.text
        self.second_name = self.ids.second_name.text
        self.date_of_birth = self.ids.date_of_birth.text
        try:
            if self.first_name == "":
                Signup_Screen_user.invalidates.append("first name")
            if self.second_name == "":
                Signup_Screen_user.invalidates.append("second name")
            if self.date_of_birth == 'Date Picker':
                Signup_Screen_user.invalidates.append("date")

            print(Signup_Screen_user.invalidates)
            date = self.ids.date_of_birth.text
            date = date.split('-')
            try:
                self.age = int(self.age_calculate(year=int(date[0]), month=int(date[1]), date=int(date[2])))
                print(self.age)
                if self.age <= 4:
                    raise ValueError
            except ValueError:
                if not Signup_Screen_user.invalidates.__contains__("date"):
                    Signup_Screen_user.invalidates.append("date")
            else:
                if Signup_Screen_user.invalidates.__contains__("date"):
                    Signup_Screen_user.invalidates.remove("date")

        except:
            pass

        if not Signup_Screen_user.invalidates:
            store = JsonStore("users.json")
            email = store.store_keys()[0]
            user_dict = store[email]
            missed = user_dict[user]["Missed_Calculation"]

            if self.CONFIRM_with_list() and not self.exists():
                color = self.ids.color.color
                self.dict = {
                    "Second_name": self.second_name,
                    "Color": color,
                    "Date_of_birth": self.date_of_birth,
                    "Level": self.level,
                    "Missed_Calculation": missed,
                }

                store = JsonStore("users.json")
                email = store.store_keys()[0]
                original = store[email]
                original[user] = self.d
                print(color)
                print(self.dict)
                store.clear()
                store[email] = original
                store = JsonStore("users.json")
                email = store.store_keys()[0]
                orig = store[email]
                orig[user]["Color"] = color
                store.clear()
                store[email] = orig
                if online():
                    t = threading.Thread(target=update)
                    t.start()
                self.ids.change_users.text = "Successfully Changed"

        else:
            Invalids(Signup_Screen_user.invalidates).open()

    def exists(self):
        user_list = []
        store = JsonStore("users.json")
        users = store.get(store.store_keys()[0])
        for u in users:
            if type(users[u]) == dict:
                user_list.append(u)
        if user_list.__contains__(self.first_name):
            return True

    def CONFIRM_with_list(self):
        try:
            print("CALLED")
            store = JsonStore("users.json")
            users = []

            users_list = store.get(store.store_keys()[0])
            print(users_list)
            for l in users_list:
                if type(users_list[l]) == dict:
                    users.append(l)
            if len(users) >= 4:
                Max_User().open()
                return False
            else:
                if users.__contains__(self.first_name):
                    return False
                else:
                    return True
        except:
            pass

    def date_picker(self):

        try:
            date = datetime.date(",".join(self.ids.date_of_birth.text.split('-')))
            print(date)
        except:
            self.ids.date_of_birth.text = "Date Picker"
        else:
            date = self.ids.date_of_birth.text.split("-")
            try:
                today = datetime.datetime.today()
                self.date_dialog = MDDatePicker(
                    min_year=today.year - 16,
                    year=date[0],
                    month=date[1],
                    day=date[2])
                self.date_dialog.open()
            except RecursionError:
                self.date_dialog.dismiss()
            self.date_dialog.bind(on_save=self.on_save)
        finally:
            today = datetime.date.today()
            self.date_dialog.min_year = today.year - 16
            self.date_dialog.open()

            self.date_dialog.bind(on_save=self.on_save)

    def age_calculate(self, year, month, date):
        print(year, month, date)
        date_today = datetime.date.today()
        date_of_birth = datetime.date(year, month, date)
        days = date_today - date_of_birth
        days = f"{days / 365}".split(",")
        days = days[0]
        years = days.split(" ")[0]
        return years

    def on_save(self, instance, value, date_range):
        date = self.ids.date_of_birth.text = str(value)
        date = date.split('-')
        date = list(date)
        print(date)

        try:
            self.age = int(self.age_calculate(year=int(date[0]), month=int(date[1]), date=int(date[2])))
            print(self.age)
            if self.age <= 4:
                raise ValueError
        except ValueError:
            if not Signup_Screen_user.invalidates.__contains__("date"):
                Signup_Screen_user.invalidates.append("date")
        else:
            if Signup_Screen_user.invalidates.__contains__("date"):
                Signup_Screen_user.invalidates.remove("date")

    def color_randomize(self):
        color = [random.uniform(0.0, 1.0) for _ in range(3)]
        con_color = [1.0 - c for c in color]
        con_color.pop()
        color.append(1.0)

        con_color.append(1.0)
        self.ids.color.background_normal = ""
        self.ids.color.background_color = con_color
        self.ids.color.color = color


class Admin_Modify(Screen):
    def __init__(self, **kwargs):
        super(Admin_Modify, self).__init__(**kwargs)
        store = JsonStore("users.json")
        self.dict = {}
        self.email = self.ids.email.text
        self.passwrd = ''
        self.orig_email = " "
        self.orig_ssd = ""

    def on_enter(self, *args):
        store = JsonStore("users.json")
        email = store.store_keys()[0]
        self.ids.email.text = email
        self.ids.change.text = "CHANGE"
        self.orig_email = store.store_keys()[0]
        self.orig_ssd = store[self.orig_email]["SSD"]

    def update_admin(self):
        SSD = self.orig_ssd
        print(SSD)
        auth.delete_user(SSD)
        auth.create_user(uid=self.passwrd, email=self.email, password=self.passwrd)
        ref = db.reference("/")
        former_data = ref.child(SSD).get()
        ref.child(SSD).delete()
        ref.child(self.passwrd).set(former_data)

    invalidates = []

    def email_validate(self, email):
        import re
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def validate(self):
        Signup_Screen.invalidates = []
        self.passwrd = hashlib.pbkdf2_hmac('sha256', self.ids.email.text.encode(), self.ids.password.text.encode(),
                                           iterations=7777).hex()
        self.email = self.ids.email.text
        try:
            if not self.email_validate(self.email):
                Signup_Screen.invalidates.append("email")
        except:
            pass
        if not Signup_Screen.invalidates:
            if online():
                self.update_admin()
            self.ids.change.text = "Successfully Changed"
        else:
            Invalids(Signup_Screen.invalidates).open()

        # email validation
        # internet error
        # fireBase

    def save(self):
        """"
        saave user and database

        """
        pass


class Sara_Tutor_App(MDApp):

    def build(self):
        global one
        # ("Armani",ZAMBEZI= z)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.accent_palette = "Red"
        root = Screen_Manager()
        one = True

        return root


# from display import Calculation_Screen
# This is a sample Python script

# handless calculation and levels


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    player_pre()
    Sara_Tutor_App().run()
    print('SORRY AN ERROR HAS OCCURED')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
""""
USER_CHOOSE
    ADD---->SIGN UP USER_SCREEN
    SETTINGS---->PROFILE
            _---->ADMIN-->LOGIN

    IF NO USER
        LOGIN SCREEN
USER_CHOOSE------>INTRODUCTION SCREEN
    ADD:-->self.age_COUNTER
    self.NAME
    Capitalize
INTRODUCTION SCREEN------>CALCULATION_SCREEN    
_-------->SAVE CHANGES
_--------->EMAIL
_-------->SYS.EXIT
PASSWORD VERIFICATION
______-DONE
EMAIL ERRORS:
    NO NETWORK
    INVALID EMAIL
"""
"""
WEB_SARA
    ___UPLOAD FILE JSON
    READ___FILE
    ACTIVATE ACCOUNT()
    ACTIVATE_DURATION
    LOAD_HTML_PAGE_OF_ID

"""
"""
AGE
LEVEL
MISSED CALCULATION
TRIALS
"""
"""
max_users
user_exists
"""
"""
background_image
purple
complete full routed
settings
add



"""
