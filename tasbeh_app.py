from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
import json, requests, os, threading

# --- Long press button classes (saqlagan ko'rinishni qoldiradi, faqat long-press qo'shiladi) ---
class LongPressRaisedButton(MDRaisedButton):
    value=0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._press_clock = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # 1 soniya ushlab tursa long_press chaqiriladi
            self._press_clock = Clock.schedule_once(self.long_press, 1.0)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # agar qisqa bosilgan bo'lsa long-press bekor qilinsin
        if self._press_clock:
            self._press_clock.cancel()
            self._press_clock = None
        return super().on_touch_up(touch)

    def long_press(self, dt):
        # app.special() ni chaqiramiz
        MDApp.get_running_app().special(self.value)


class LongPressIconButton(MDIconButton):
    value=0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._press_clock = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._press_clock = Clock.schedule_once(self.long_press, 3.0)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._press_clock:
            self._press_clock.cancel()
            self._press_clock = None
        return super().on_touch_up(touch)

    def long_press(self, dt):
        app = MDApp.get_running_app()
        if self.value == 40:  # maxsus tugma
            on_dev_long_press(app,
                              default_link="https://github.com/your/default",
                              pin="1423",
                              link_key="dev_link")
        else:
            app.special(self.value)


KV = """
ScreenManager:
    MDScreen:
        name: 'mask'
        id: mask_scr
        md_bg_color: 1,1,0,0.8
        MDLabel:
            id: val_save
            text: ''
            font_size: '40sp'
            halign: 'center'
            valign: 'center'
            pos_hint: {"center_x": .5, "center_y": .93}
        MDLabel:
            id: count
            text: '0'
            font_size: '100sp'
            halign: 'center'
            valign: 'center'
            pos_hint: {"center_x": .5, "center_y": .7}
        MDGridLayout:
            rows: 3
            size_hint: 0.5,0.5
            pos_hint: {"center_x": .58, "center_y": .35}
            padding: dp(30)
            spacing: dp(30)
            MDRaisedButton:
                text: '-'
                font_size: '30sp'
                on_release: app.counter(self.text)
            # <-- 0 tugmasi endi LongPressRaisedButton -->
            LongPressRaisedButton:
                text: '0'
                value: 7
                font_size: '30sp'
                on_release: root.ids.count.text='0'
            MDRaisedButton:
                text: '+'
                font_size: '30sp'
                on_release: app.counter(self.text)

        # <-- SAQLASH tugmasi endi LongPressRaisedButton -->
        LongPressRaisedButton:
            text: 'SAQLASH'
            value: 8
            size_hint: 0.5,0.07
            pos_hint: {"center_x": .5, "center_y": .13}
            on_release: app.value_save()

        # <-- TOZALASH tugmasi endi LongPressRaisedButton -->
        LongPressRaisedButton:
            md_bg_color: 1,0,0,0.8
            text: 'TOZALASH'
            value: 3
            theme_text_color: 'Custom'
            text_color: 0.8,0.8,0,1
            size_hint: 0.5,0.07
            pos_hint: {"center_x": .5, "center_y": .05}
            on_release: app.detect()

        MDIconButton:
            icon: 'logout'
            theme_icon_color: 'Custom'
            icon_color: 0.7,0,0,1
            md_bg_color: 0.9,0.9,0,1
            icon_size: '30sp'
            pos_hint: {"center_x": .9, "center_y": .09}
            on_release: app.exit()


    MDScreen:
        name: 'main'
        FloatLayout:
            MDLabel:
                id: main_lbl
                halign: 'justify'
                valign: 'middle'
                text: ''
                text_size: self.width-dp(20), None
                size_hint: 1, 1
                padding: dp(10), dp(10)
                theme_text_color: 'Primary'
                font_style: 'H6'

        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(20)
            size_hint: 1, 0.01
            pos_hint: {"center_x": .5, "center_y": .07}

            GridLayout:
                rows: 1
                size_hint: 1,0.15
                pos_hint: {"center_x": .5, "center_y": .07}
                spacing: dp(5)
                padding: dp(5)

                MDRaisedButton:
                    text: 'MANBA'
                    size_hint_y: 0.5
                    font_size: '16sp'
                    on_release: app.root.current = "manba"
                MDRaisedButton:
                    text: 'XOBARIY'
                    size_hint_y: 0.5
                    font_size: '16sp'
                    on_release:
                        app.root.current = "xobariy"
                        app.menu_btn('xobariy_buttons', 'xobariy')
                MDRaisedButton:
                    text: 'ASLIY'
                    size_hint_y: 0.5
                    font_size: '16sp'
                    on_release:
                        app.root.current = "asliy"
                        app.menu_btn('asliy_buttons', 'asliy')

        FloatLayout:
            LongPressIconButton:
                id: menu
                value: 40
                icon: 'menu'
                theme_icon_color: 'Custom'
                icon_color: 0,0.5,0,1
                icon_size: "40sp"
                pos_hint: {"center_x": .094, "center_y": .97}
                on_release: app.root.current = "menu"

    MDScreen:
        name: 'menu'
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(20)
            size_hint: 1, 1
            pos_hint: {"center_x": .5, "center_y": .5}
        GridLayout:
            cols: 1
            size_hint: 0.5, 0.5
            pos_hint: {"center_x": .68, "center_y": .57}
            spacing: dp(30)
            MDIconButton:
                icon: 'eye-off'
                id: hide_btn
                theme_icon_color: 'Custom'
                icon_size: '40sp'
                icon_color: 0.7,0,0,1
                md_bg_color: 1,1,0,1
                on_release:
                    app.force_enable_security();
                    root.current="mask"
                    #############
            MDIconButton:
                icon: 'toggle-switch'
                id: security_btn
                theme_icon_color: 'Custom'
                icon_color: 0,0.9,0,1
                icon_size: '35sp'
                on_release: app.security()
            MDIconButton:
                icon: 'home'
                id: home_btn
                theme_icon_color: 'Custom'
                icon_size: '35sp'
                on_release: app.root.current = "main"
            MDIconButton:
                id: dark_light
                icon: 'brightness-6'
                theme_icon_color: 'Custom'
                icon_size: '35sp'
                on_release: app.toggle_theme()
            MDIconButton:
                id: refresh
                icon: 'update'
                theme_icon_color: 'Custom'
                icon_size: '35sp'
                on_release: app.update_json()
            MDSpinner:
                id: spinner
                size_hint: None, None
                size: dp(46), dp(46)
                pos_hint: {'center_x':.5, 'center_y':.9}
                active: False
            MDIconButton:
                icon: 'logout'
                theme_icon_color: 'Custom'
                icon_size: '35sp'
                on_release: app.exit()

    MDScreen:
        name: 'asliy'
        BoxLayout:
            orientation: 'vertical'
            ScrollView:
                MDGridLayout:
                    id: asliy_buttons
                    cols: 1
                    spacing: dp(10)
                    padding: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

        GridLayout:
            cols: 1
            size_hint: 0.5, 0.5
            pos_hint: {"center_x": .25, "center_y": .75}
            spacing: dp(30)
            MDIconButton:
                icon: 'chevron-left'
                id: back_btn
                theme_icon_color: 'Custom'
                icon_size: '40sp'
                on_release: app.root.current = "main"

    MDScreen:
        name: 'xobariy'
        BoxLayout:
            orientation: 'vertical'
            ScrollView:
                MDGridLayout:
                    id: xobariy_buttons
                    cols: 1
                    spacing: dp(10)
                    padding: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

        GridLayout:
            cols: 1
            size_hint: 0.5, 0.5
            pos_hint: {"center_x": .25, "center_y": .75}
            spacing: dp(30)
            MDIconButton:
                icon: 'chevron-left'
                id: back_btn
                theme_icon_color: 'Custom'
                icon_size: '40sp'
                on_release: app.root.current = "main"

    MDScreen:
        name: 'manba'
        BoxLayout:
            orientation: 'vertical'
            ScrollView:
                MDGridLayout:
                    id: manba_buttons
                    cols: 1
                    spacing: dp(10)
                    padding: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

        GridLayout:
            cols: 1
            size_hint: 0.5, 0.5
            pos_hint: {"center_x": .25, "center_y": .75}
            spacing: dp(30)
            MDIconButton:
                icon: 'chevron-left'
                theme_icon_color: 'Custom'
                icon_size: '40sp'
                on_release: app.root.current = "main"
"""

# --- uzun bosilganda PIN dialog ---
def on_dev_long_press(app, default_link, pin="1423", link_key="dev_link"):
    import time
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.button import MDFlatButton
    from kivymd.uix.textfield import MDTextField
    from kivymd.toast import toast

    # check lock
    now = time.time()
    if hasattr(app, "_dev_locked_until") and app._dev_locked_until > now:
        toast(f"Urinish bloklangan! {int((app._dev_locked_until-now)//60)} daqiqa qoldi")
        return

    # dialog
    content = MDTextField(
        hint_text="PINni kiriting",
        password=True,
        size_hint_y=None,
        height="40dp"
    )

    def on_submit(instance):
        entered_pin = content.text
        dialog.dismiss()
        check_dev_pin(app, entered_pin, max_attempts=3, lock_duration=3600,
                      pin=pin, link_key=link_key, default_link=default_link)

    dialog = MDDialog(
        title="PINni kiriting",
        type="custom",
        content_cls=content,
        buttons=[
            MDFlatButton(text="OK", on_release=lambda x: on_submit(x)),
            MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss())
        ]
    )
    dialog.open()


def check_dev_pin(app, entered_pin, max_attempts, lock_duration, pin, link_key, default_link):
    from kivymd.toast import toast
    import time

    # JsonStore’dan olish, agar mavjud bo‘lmasa default qiymat
    lock_data = app.store.get("dev_lock") if app.store.exists("dev_lock") else {}
    attempts = lock_data.get("attempts", 0)
    locked_until = lock_data.get("locked_until", 0)

    now = time.time()
    if locked_until > now:
        toast(f"Urinish bloklangan! {int((locked_until-now)//60)} daqiqa qoldi")
        return

    if entered_pin == pin:
        attempts = 0
        # jsondagi linkni tekshirish
        url = app.all_topics.get(link_key, default_link)
        app.open_url(url)
        toast("To'g'ri PIN, link ochildi ✅")
    else:
        attempts += 1
        if attempts >= max_attempts:
            locked_until = now + lock_duration
            attempts = 0
            toast(f"3 urinish xato! 1 soatga bloklandi ❌")
        else:
            toast(f"PIN xato! {max_attempts - attempts} urinish qoldi")

    # JsonStore’ga saqlash
    app.store.put("dev_lock", attempts=attempts, locked_until=locked_until)


class Tavhiyd(MDApp):
    def build(self):
        self.store = JsonStore("settings.json")
        theme = self.store.get("theme")["style"] if self.store.exists("theme") else "Dark"
        self.theme_cls.theme_style = theme

        self.value = 0
        self.sp = 0
        self.scrt=True
        
        APP_DIR =os.path.join(os.path.expanduser('~'), 'myapp_data')
        os.makedirs(APP_DIR, exist_ok=True)
        self.json_path=os.path.join(APP_DIR, 'topics.json')
        #'/storage/emulated/0/download/pydroid 3/topics.json'

        # xavfsiz yuklash: fayl bo'lmasa bo'sh dict bilan davom etamiz
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.all_topics = json.load(f)
        except Exception as e:
            print("topics.json load error:", e)
            self.all_topics = {}
        if not self.store.exists('dev_lock'):
            self.store.put('dev_lock', attemps=0, locked_until=0)

        return Builder.load_string(KV)

    def on_start(self):
        self.root.ids.main_lbl.text = (
            "Mehribon va rahmli ALLAH nomi bilan!\n\n"
            "Ahli Tavhiydga Assalamu alaykum va rohmatullahi va barokatuh!\n\n"
            "Ushbu ilova ALLAH huzuridagi yagona diyn bo`lmish ISLAM diynini "
            "ALLAHning qullariga sof holatda yetkazish uchun xolis tarzda ishlab chiqildi.\n\n"
            "Birorta xato yoki kamchiliklar topilsa darhol bizga xabar bering!"
        )
        self.ensure_json()
        #self.load_manba_buttons()


    def ensure_json(self):
        if not os.path.exists(self.json_path):
            from kivy.clock import Clock
            import threading
            Clock.schedule_once(lambda dt: self.show_message("JSON yo‘q, yuklanmoqda..."), 0)
            threading.Thread(target=self._do_update, daemon=True).start()
        else:
            # mavjud bo'lsa faylni o'qish
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.all_topics = json.load(f)
            self.load_manba_buttons()


    def load_manba_buttons(self):
        container = self.root.ids.manba_buttons
        container.clear_widgets()
        for item in self.all_topics.get("manba", []):
            btn = MDRaisedButton(
                text=item.get('title', 'No title'),
                size_hint=(0.7, None),
                height=dp(40),
                pos_hint={'center_x': 0.5},
                on_release=lambda x, url=item.get('url', ''): self.open_url(url)
            )
            container.add_widget(btn)

    def counter(self, val):
        if val == '+':
            self.value += 1
        else:
            if self.value > 0:
                self.value -= 1
        # agar main ekranda bo'lsa ids mavjud bo'ladi
        try:
            self.root.ids.count.text = str(self.value)
        except Exception:
            pass

    def value_save(self):
        try:
            val1 = self.root.ids.count.text
            val2 = self.root.ids.val_save.text
            if not val2:
                val2 = '0'
            self.root.ids.val_save.text = str(int(val1) + int(val2))
            toast("Saqlandi")
        except Exception:
            toast("Saqlashda xatolik")

    def force_enable_security(self):
        """Xavfsizlik tugmasini faqat ko‘rinishda yoqadi, taymerni chaqirmaydi"""
        scrt_btn = self.root.ids.security_btn
        self.scrt = True
        scrt_btn.icon = 'toggle-switch'
        scrt_btn.icon_color = 0, 0.9, 0, 1

    # --- Xavfsizlik tugmasi ---
    def security(self):
        scrt_btn = self.root.ids.security_btn
        self.scrt = not getattr(self, "scrt", False)

        if self.scrt:
            scrt_btn.icon = 'toggle-switch'
            scrt_btn.icon_color = 0, 0.9, 0, 1
            toast("Xavfsizlik rejimi yoqildi")
            # xavfsizlik yoqilganda taymerni ishga tushiramiz
            
            self.show_hidden_security(0)
            
        else:
            scrt_btn.icon = 'toggle-switch-off'
            scrt_btn.icon_color = 0.9, 0, 0, 1
            toast("Xavfsizlik rejimi oʻchirildi")
            # xavfsizlik o‘chirilsa, barcha taymerlarni bekor qilamiz
            if hasattr(self, 'hidden_timer') and self.hidden_timer:
                self.hidden_timer.cancel()
            if hasattr(self, 'security_dialog') and self.security_dialog:
                self.security_dialog.dismiss()
                self.security_dialog = None


    # --- Xavfsizlik alerti va yashirin bo‘lim taymeri ---
    def show_hidden_security(self, alert_duration=60, mask_duration=600):
        self.hidden_stop_pressed=False
        """
        alert_duration = dialog chiqish vaqti (soniya)
        mask_duration = dialog yopilgach, maskga o'tish vaqti
        """
        if not getattr(self, "scrt", False):
            return  # xavfsizlik rejimi o‘chiq bo‘lsa ishlamaydi

        if hasattr(self, 'hidden_timer') and self.hidden_timer:
            self.hidden_timer.cancel()

        # alert_duration soniyadan keyin alert chiqadi
        self.hidden_timer = Clock.schedule_once(
            lambda dt: self._security_alert(mask_duration), alert_duration
        )


    def _security_alert(self, mask_duration):
        from kivymd.uix.button import MDFlatButton

        if not getattr(self, "scrt", False):
            return  # xavfsizlik rejimi o‘chiq bo‘lsa ishlamaydi

        if hasattr(self, 'security_dialog') and self.security_dialog:
            self.security_dialog.dismiss()

        self.security_dialog = MDDialog(
            title="Xavfsizlik ogohlantirishi",
            text="Niqoblanish rejimiga 1 daqiqa qoldi.\n"
                 "Jarayonni to‘xtatmoqchi bo‘lsangiz STOP tugmasini bosing, "
                 "aks holda xabarni e’tiborsiz qoldiring.",
            buttons=[
                MDFlatButton(
                    text="STOP",
                    on_release=lambda x: self.stop_hidden_timer(mask_duration)
                )
            ]
        )
        self.security_dialog.bind(
            on_dismiss=lambda inst: self._schedule_mask(mask_duration) if not self.hidden_stop_pressed else None
        )
        self.security_dialog.open()


    def _schedule_mask(self, mask_duration):
        """
        Agar dialog yopilgan bo‘lsa va STOP bosilmagan bo‘lsa,
        yana mask_duration sekunddan keyin mask ekranga o'tadi
        """
        if not getattr(self, "scrt", False):
            return  # xavfsizlik rejimi o‘chiq bo‘lsa ishlamaydi

        if hasattr(self, 'hidden_timer') and self.hidden_timer:
            self.hidden_timer.cancel()

        self.hidden_timer = Clock.schedule_once(self._apply_mask, mask_duration)


    def _apply_mask(self, dt):
        """
        Dialogdan keyin yoki timer tugagach, mask ekranga o'tadi
        """
        if not getattr(self, "scrt", False):
            return  # xavfsizlik rejimi o‘chiq bo‘lsa ishlamaydi

        self.root.current = "mask"
        toast("Xavfsizlik: Niqoblanish rejimiga o'tildi")


    def stop_hidden_timer(self, mask_duration):
        self.hidden_stop_pressed = True

        if hasattr(self, 'hidden_timer') and self.hidden_timer:
            self.hidden_timer.cancel()

        if not getattr(self, "scrt", False):
            return  # xavfsizlik rejimi o‘chiq bo‘lsa qayta ishga tushirmaydi

        # qayta 10 soniyaga taymerni ishga tushiramiz
        def _restart_alert(dt):
            self.hidden_stop_pressed = False   # <--- MUHIM!
            self._security_alert(mask_duration)

        self.hidden_timer = Clock.schedule_once(_restart_alert, 600)

        if hasattr(self, 'security_dialog') and self.security_dialog:
            self.security_dialog.dismiss()
            self.security_dialog = None

        toast("Jarayon to‘xtatildi, 10 daqiqalik taymer qayta set qilindi")

    def detect(self):
        if self.root.ids.val_save.text == '7':
            if self.root.ids.count.text == '8':
                self.root.current = "main"
                self.show_hidden_security(300)
                toast("Yashirin bo'lim ochildi")
                self.root.ids.count.text = "0"
                self.value = 0
        self.root.ids.val_save.text = ""

    def toggle_theme(self):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            toast("Qorongʻu rejim")
        else:
            self.theme_cls.theme_style = "Light"
            toast("Yorugʻ rejim")
        self.store.put("theme", style=self.theme_cls.theme_style)

    def special(self, value):
        # long-press natijasi: maxsus funktsionallik
        if value == 3:
            toast("TOZALASH (3)")
        elif value == 7:
            toast("0 (7)")
        elif value == 8:
            toast("SAQLASH (8)")

        self.sp += value

        # Eski taymerni bekor qilamiz, agar foydalanuvchi davom etsa
        if hasattr(self, "_reset_event") and self._reset_event:
            self._reset_event.cancel()

        if self.sp == 18:
            self.root.current = "main"
            self.show_hidden_security(300)
            toast("Yashirin boʻlim ochildi!")
            self.sp = 0
        elif self.sp > 18:
            self.sp = 0
            toast("TOZALANDI")
        else:
            # Agar 10 soniyada yig‘indi 18 ga teng bo‘lmasa, nolga qaytadi
            self._reset_event = Clock.schedule_once(lambda dt: self._reset_sp(), 10)

    def _reset_sp(self):
        self.sp = 0
        toast("TOZALANDI!")

    def open_url(self, url):
        
        try:
            requests.get('https://www.google.com', timeout=5)
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self.show_message('Internet mavjud emas!'), 0)
            return
            
        if not url:
            toast("URL mavjud emas")
            return
            
        import webbrowser
        webbrowser.open(url)

    def menu_btn(self, btn_id, name):
        container = self.root.ids[btn_id]
        container.clear_widgets()

        topics = self.all_topics.get(name, [])
        for topic in topics:
            btn = MDRaisedButton(
                text=topic.get('title', 'No title'),
                pos_hint={'center_x': 0.5},
                size_hint=(0.7, None),
                height=dp(40),
                on_release=lambda x, t=topic: self.show_topic(t)
            )
            container.add_widget(btn)

    def show_topic(self, topic):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title=topic.get('title', ''),
            type="custom",
            content_cls=MDLabel(
                text=topic.get('content', ''),
                halign="center",
                size_hint_y=None
            ),
            buttons=[]
        )
        self.dialog.content_cls.texture_update()
        self.dialog.content_cls.height = self.dialog.content_cls.texture_size[1] + dp(20)
        self.dialog.open()

    def show_message(self, text):
        toast(text)

    def update_json(self):
        # boshlanishida spinner yoq
        try:
            self.root.ids.spinner.active = True
        except Exception:
            pass
        toast("Yuklanmoqda...")
        threading.Thread(target=self._do_update, daemon=True).start()

    def _do_update(self):
        import requests
        from kivy.clock import Clock

        try:
            requests.get('https://www.google.com', timeout=5)
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self.show_message('Internet mavjud emas!'), 0)
            return

        urls = self.all_topics.get("update_links", [])
        if not urls:
            urls = [
                "https://www.dropbox.com/scl/fi/yoqhqts1ymdglzltjuj16/topics.json?dl=1",
                "https://raw.githubusercontent.com/rozimuradovbehruz/Database-files/main/topics.json"
            ]

        new_data = None
        for url in urls:
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                new_data = r.json()
                break
            except Exception as e:
                print(f"URL ishlamadi: {url} | xato: {e}")

        if new_data:
            import os, json
            try:
                temp_path = self.json_path + ".tmp"
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=2)
                os.replace(temp_path, self.json_path)
                self.all_topics = new_data
                Clock.schedule_once(lambda dt: self.show_message("Ma'lumotlar yangilandi ✅"), 0)
                Clock.schedule_once(lambda dt: self.load_manba_buttons(), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_message("Faylni saqlashda xato ❌"), 0)
        else:
            Clock.schedule_once(lambda dt: self.show_message("Yangilashda xato ❌"), 0)
        Clock.schedule_once(lambda dt: self._stop_spinner(), 0)

    def load_manba_buttons(self):
        container = self.root.ids.manba_buttons
        container.clear_widgets()
        for item in self.all_topics.get("manba", []):
            btn = MDRaisedButton(
                text=item.get('title', 'No title'),
                size_hint=(0.7, None),
                height=dp(40),
                pos_hint={'center_x': 0.5},
                on_release=lambda x, url=item.get('url', ''): self.open_url(url)
            )
            container.add_widget(btn)

    def _stop_spinner(self):
        try:
            self.root.ids.spinner.active = False
        except Exception:
            pass

    def exit(self):
        self.stop()


if __name__ == '__main__':
    Tavhiyd().run()