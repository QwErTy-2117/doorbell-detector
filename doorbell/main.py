from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock, mainthread

from pythonosc import dispatcher as osc_dispatcher, osc_server
import threading

OSC_SERVICE_PORT = 3000  # service sends to this port
OSC_UI_PORT = 3001       # UI receives on this port


class DoorbellApp(App):

    def build(self):
        root = BoxLayout(orientation="vertical", padding=32, spacing=16)

        self.status_label = Label(
            text="Inactive",
            font_size="18sp",
            color=(0.6, 0.6, 0.6, 1),
        )
        self.score_label = Label(
            text="",
            font_size="14sp",
            color=(0.5, 0.5, 0.5, 1),
        )
        self.toggle = ToggleButton(
            text="Start Listening",
            size_hint=(1, None),
            height="56dp",
            font_size="18sp",
        )
        self.toggle.bind(on_press=self.on_toggle)

        root.add_widget(self.status_label)
        root.add_widget(self.score_label)
        root.add_widget(self.toggle)

        self._start_osc_server()
        return root

    def on_toggle(self, btn):
        if btn.state == "down":
            btn.text = "Listening…"
            self._start_service()
            self.status_label.text  = "Listening for doorbell"
            self.status_label.color = (0.2, 0.8, 0.4, 1)
        else:
            btn.text = "Start Listening"
            self._stop_service()
            self.status_label.text  = "Inactive"
            self.status_label.color = (0.6, 0.6, 0.6, 1)
            self.score_label.text   = ""

    def _start_service(self):
        from android import mActivity
        from jnius import autoclass
        SERVICE_CLASS = f"{self.get_application_name()}.ServiceService"
        Intent = autoclass("android.content.Intent")
        intent = Intent()
        intent.setClassName(mActivity, SERVICE_CLASS)
        mActivity.startForegroundService(intent)

    def _stop_service(self):
        from android import mActivity
        from jnius import autoclass
        SERVICE_CLASS = f"{self.get_application_name()}.ServiceService"
        Intent = autoclass("android.content.Intent")
        intent = Intent()
        intent.setClassName(mActivity, SERVICE_CLASS)
        mActivity.stopService(intent)

    def _start_osc_server(self):
        d = osc_dispatcher.Dispatcher()
        d.map("/status", self._on_status)
        d.map("/alert",  self._on_alert)
        server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", OSC_UI_PORT), d)
        threading.Thread(target=server.serve_forever, daemon=True).start()

    @mainthread
    def _on_status(self, address, top_label, doorbell_score, mean_score):
        self.score_label.text = (
            f"Top: {top_label:<28}  |  doorbell: {doorbell_score:.2f}  (avg {mean_score:.2f})"
        )

    @mainthread
    def _on_alert(self, address, value):
        self.status_label.text  = "Doorbell detected!"
        self.status_label.color = (1.0, 0.6, 0.1, 1)
        Clock.schedule_once(
            lambda dt: setattr(self.status_label, "text", "Listening for doorbell"), 4
        )


if __name__ == "__main__":
    DoorbellApp().run()