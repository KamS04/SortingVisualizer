if __name__ == '__main__':
    from time import sleep
    import cProfile
    from kivy.config import Config
    Config.set('graphics', 'resizable', False)

    import kivy
    kivy.require('1.11.1')

    from kivy.core.window import Window
    from kivy.app import App
    from kivy.uix.widget import Widget
    from kivy.uix.floatlayout import FloatLayout
    from kivy.properties import NumericProperty, ObjectProperty, ListProperty, StringProperty
    from kivy.clock import Clock
    from kivy.graphics import Color, Rectangle

    import random
    import multiprocessing

    import algorithms

    # ------ DATA ---------
    _first_resize = False

    # ---- Classes ----

    class RadioButton(FloatLayout):
        group = ObjectProperty(None)
        text = StringProperty("")
        _check_box = ObjectProperty(None)
        selected_input = ObjectProperty(None)
        selected_val = StringProperty("")

        def on_kv_post(self, base_widget):
            print(self._check_box)
            self._check_box.bind(active=self.state_changed)
            if self not in self.group:
                self.group.append(self)

        def state_changed(self, check_box, value):
            if value:
                for cbox in self.group:
                    if cbox is not self:
                        cbox._check_box.active = False
                self.selected_input[0] = self.selected_val

    class Visualizer(Widget):
        _margin = 15    
        bar_width = 1
        sorter = None
        sleep_time = 0.001

        def init(self):
            #self.size = (self.size[0], self.size[0])
            self.lock = multiprocessing.Lock()
            self.manager = multiprocessing.Manager()
            self.data = self.manager.list(self.gen_data())
            self.processes = self.manager.list()
            Clock.schedule_interval(self.draw, 0)
            self.is_sorting = False

        def reset(self, bar_width=None):
            if bar_width is not None:
                self.bar_width = bar_width
            if self.sorter is not None and self.sorter.is_alive():
                self.sorter.terminate()
                self.sorter.join()
                self.is_sorting = False
            self.lock.acquire()
            self.data = self.manager.list(self.gen_data())
            self.lock.release()

        def gen_data(self):
            return [random.randint(1, int(self.size[0] - self._margin * 2)) for i in range(int((self.size[0] - self._margin * 2)//self.bar_width))]

        def get_max_height(self):
            return self.size[1] - self._margin * 2

        def get_max_width(self):
            return (self.size[0] - self._margin * 2) // 5

        def draw(self, *args):
            self.canvas.clear()
            x = []
            with self.canvas:
                self.lock.acquire()
                display_data = list(self.data)
                self.lock.release()
                for i, v in enumerate(display_data):
                    Color(10, 10, 10)
                    Rectangle(size=(self.bar_width, v), pos=(self.pos[0] + self._margin + (self.bar_width * i), self._margin))
                    x.append(self.pos[0] + self._margin + self.bar_width * i)

        def start_sort(self, algorithm):
            if self.sorter is not None and self.sorter.is_alive():
                self.sorter.terminate()
                #self.sorter.join()
                self.is_sorting = False
                self.reset()
            if algorithm in algorithms.algorithm_map.keys():
                alg = algorithms.algorithm_map[algorithm]
                self.sorter = multiprocessing.Process(target=alg, args=(self.data, self.lock, self.processes, self.sleep_time), daemon=True)
                self.is_sorting = True
                self.sorter.start()

        def kill_sort(self):
            if self.sorter is not None and self.sorter.is_alive():
                self.sorter.terminate()
                #self.sorter.join()
                self.is_sorting = False

    class SortingVisualizerApp(App):
        visualizer = ObjectProperty(None)
        slider = ObjectProperty(None)
        sorting_radio_group = ListProperty([])
        selected_algorithm = ListProperty(['BubbleSort'])

        def on_start(self):
            Window.size = (800, 600)
            self.visualizer = self.root.ids['visualizer']
            self.slider = self.root.ids['width_control']
            self.visualizer.bind(size=self.size_changed)
            self._profile = cProfile.Profile()
            self._profile.enable()
        
        def setup(self):
            self.visualizer.init()
            self.setup_size_slider()
            
        def reset_arrays(self, *args):
            self.visualizer.reset()

        def size_changed(self, *args):
            global _first_resize
            if not _first_resize:
                self.visualizer.unbind(size=self.size_changed)
                _first_resize = True
                self.setup()

        def setup_size_slider(self):
            max_width = self.visualizer.get_max_width()
            self.slider.max = max_width
            self.slider.min = 1
            self.slider.bind(value=self.width_control_changed)

        def width_control_changed(self, controller, value):
            self.visualizer.reset(bar_width=int(value))
            self.root.ids['width_display'].text = str(int(value))

        def start_sort(self, *args):
            print("starting sort")
            self.visualizer.start_sort(self.selected_algorithm[0])

        def on_stop(self):
            self._profile.disable()
            self._profile.dump_stats('storvis.profile')

    multiprocessing.freeze_support()
    app = SortingVisualizerApp()
    app.run()