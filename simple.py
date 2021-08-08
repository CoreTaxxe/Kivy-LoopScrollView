from kivy.app import App
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stencilview import StencilView
from kivy.properties import NumericProperty, ListProperty, StringProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.core.window import Window

Builder.load_string("""
<HLabel>:
    canvas:
        Color:
            rgb : 1,1,1
        Line:
            rectangle: (*self.pos,self.width ,self.height )

<SV>:
    canvas:
        Color:
            rgb : 1,0,0
        Line:
            rectangle: (0+1,0+1,self.width - 1,self.height -1 )
            width:5

<Root>:
        
    CustomStencilView:
        id : SV
        size_hint : (0.5,0.5)
        pos_hint : {'center_x':0.5,'center_y':0.5}
        canvas:
            Color:
                rgba : 1,1,1,0
            Line:
                rectangle: (0,0,*self.size)
""")


class HLabel(Label):
    index = NumericProperty()
    data_index = NumericProperty()

    def update(self, data):
        self.text = "Label No. : " + str(self.index) + " " * 10 + "-" + " " * 10 + "Data : " + data


class SV(RelativeLayout):
    pass


class CustomStencilView(RelativeLayout):
    children_height = 44
    loop = BooleanProperty(False)
    do_overscroll = BooleanProperty(False)
    min_widgets = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CustomStencilView, self).__init__(**kwargs)

        self.data = [str(x) for x in range(15)]
        self._stencil = SV(size_hint=(None, None), size=(0, 0))

        self.bind(pos=lambda widget, value: setattr(self._stencil, "pos", (0, 0)))
        self.bind(size=lambda widget, value: self.add_data())
        self.bind(size=lambda widget, value: setattr(self._stencil, "size", value))

        self.add_widget(self._stencil, is_viewport=True)

        self._last_mouse_pos = [0, 0]
        # self.loop = True
        self.block = None
        self.do_overscroll = False

        from kivy.logger import Logger

        self.todo = [
            "Add 'self.loop' listener",
            "Add kinetic overscroll effect",
            "Add `self.size` listener"
            "Code cleanup",
            "comments",
            "scroll-to-function",
            "x - Axis- scroll",
            "scrollbars"
        ]

        for todo in self.todo:
            Logger.warning(f"LoopSV : Needs to be done : {todo}.")

    def add_widget(self, widget, index=0, canvas=None, is_viewport=False):
        """

        :param widget:
        :param index:
        :param canvas:
        :param is_viewport:
        :return:
        """
        if is_viewport:
            super(CustomStencilView, self).add_widget(widget, index, canvas)
        else:
            self._stencil.add_widget(widget, index, canvas)

    def add_data(self):

        self._stencil.clear_widgets()
        self.min_widgets = round(self.height / self.children_height) + 3

        for _ in range(self.min_widgets, 0, -1):
            _entry = HLabel(
                text=str(_ - 1),
                size_hint=(1, None),
                height=self.children_height,
                pos=(0, self.height - self.children_height * _),
                index=_ - 1,
                data_index=_ - 1
            )

            self.add_widget(_entry)
        self.refresh_from_index(0)

    def on_touch_down(self, touch):

        if touch.button == 'right':
            self.loop = not self.loop
            return

        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._last_mouse_pos = touch.pos
            return True

        return super(CustomStencilView, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            delta_x = touch.pos[0] - self._last_mouse_pos[0]
            delta_y = touch.pos[1] - self._last_mouse_pos[1]

            if delta_y > 0 and self.block == "down" or delta_y < 0 and self.block == "up":
                return
            else:
                self.do_scroll(delta_x, delta_y)

            self._last_mouse_pos = touch.pos

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            touch.ungrab(self)
            return True

        return super(CustomStencilView, self).on_touch_up(touch)

    def do_scroll(self, dx, dy):

        _children = self._stencil.children

        _top, _bot = _children[0], _children[0]

        _free = True
        for _child in _children:
            _child.y += round(dy)

            if not self.loop:
                if _child.data_index >= len(self.data) - 1 and _child.y >= 0:
                    self._trigger_overscroll('down', _child)
                    _free = False

                elif _child.data_index <= 0 and _child.y <= self.height - _child.height:
                    self._trigger_overscroll('up', _child)
                    _free = False

            _top = _child if _child.y > _top.y else _top
            _bot = _child if _child.y < _bot.y else _bot

        if _free:
            self._trigger_overscroll("free")

        if _top.y > self.height + _top.height and dy > 0:
            _top.y = _bot.y - _top.height
            self.update_child(_top, _direction="down")

        elif _bot.y < 0 - _bot.height - _bot.height and dy < 0:
            _bot.y = _top.y + _top.height
            self.update_child(_bot, _direction="up")

    def refresh_from_index(self, index=0):
        """

        :param index:
        :return:
        """
        children = self._stencil.children

        self.reset_positions(brute=True)
        for child in children:
            if index >= len(self.data) and self.loop == False:
                child.update("")
                child.data_index = index
            else:
                _data = self.data[index % len(self.data)]
                child.update(_data)
                child.data_index = index % len(self.data)
            index += 1

    def reset_positions(self, brute=True):

        children = self._stencil.children
        if brute:
            for child in children:
                child.y = self.height - (child.height * (child.index + 1))
        else:
            while children[0].y != self.height - children[0].height:
                self.do_scroll(0, 1)

    def _trigger_overscroll(self, direction, child=None):
        """

        :param direction:
        :return:
        """
        if direction == "down":
            self.block = "down"
            if child is not None:
                while child.y != 0:
                    self.do_scroll(0, 1 if child.y < 0 else -1)
        elif direction == "up":
            self.block = "up"
            if child is not None:
                while child.y != self.height - child.height:
                    self.do_scroll(0, 1 if child.y < self.height - child.height else -1)
        else:
            self.block = None

    def update_child(self, child, _direction="down"):
        """

        :param child:
        :return:
        """

        if _direction == 'down':
            _data_index = (child.data_index + self.min_widgets)
            if self.loop:
                _data_index = _data_index % len(self.data)
                child.update(self.data[_data_index])
                child.data_index = _data_index
            else:
                if _data_index >= len(self.data) or _data_index < 0:
                    child.update("")
                    child.data_index = _data_index

                else:
                    child.update(self.data[_data_index])
                    child.data_index = _data_index

        else:
            _data_index = (child.data_index - self.min_widgets)

            if self.loop:
                _data_index = _data_index % len(self.data)
                child.update(self.data[_data_index])
                child.data_index = _data_index
            else:
                if _data_index < 0 or _data_index >= len(self.data):
                    child.update("")
                    child.data_index = _data_index
                else:
                    child.update(self.data[_data_index])
                    child.data_index = _data_index


class Root(RelativeLayout):
    pass


class TestApp(App):
    def build(self):
        return Root()


if __name__ == "__main__":
    TestApp().run()
