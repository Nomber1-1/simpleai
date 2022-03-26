from enum import Enum

from browser import ajax, window

from graphs import render_graph


# javascript "imports"
jq = window.jQuery
EventSource = window.EventSource
jsjson = window.JSON


class Tab(Enum):
    """
    The tabs that the user can view.
    """
    HELP = "help"
    GRAPH = "graph"
    LOG = "log"
    STATS = "stats"


class AlgorithmAction(Enum):
    """
    The actions that we can cask to the algorithm running in the background.
    """
    PLAY = "play"
    STEP = "step"
    PAUSE = "pause"
    STOP = "stop"


class WebViewerClient:
    """
    The Web Viewer client side app itself.
    """
    def __init__(self):
        """
        Initialize the client side app.
        """
        print("Initializing Web Viewer Client...")

        jq(".control-algorithm-btn").on("click", self.on_control_algorithm_click)
        jq(".show-tab-btn").on("click", self.on_show_tab_click)
        jq("#speed-sldr").on("input", self.on_speed_slider_change)

        self.last_event = None
        self.event_log = []
        self.stats = {}

        self.stats_display = jq("#stats-display")
        self.last_event_display = jq("#last-event-display")
        self.log_display = jq("#log-display")

        self.switch_to_tab(Tab.HELP)
        self.initialize_event_stream()

        print("Web Viewer Client ready")

    def switch_to_tab(self, tab):
        """
        Show a specific tab to the user, and remember the active tab.
        """
        self.current_tab = tab
        jq(".tab").hide()
        jq(f"#tab-{tab.value}").show()

    def initialize_event_stream(self):
        """
        Start listening to the event stream from the running algorithm.
        """
        self.event_source = EventSource.new("/event_stream")
        self.event_source.onmessage = self.on_message

    def on_message(self, event):
        """
        Message received from the running algorithm.
        The "event" parameter here isn't an algorithm event, but a message
        from the web event stream.
        """
        message = jsjson.parse(event.data)
        self.register_event(message.event)
        self.register_stats(message.stats)

    def register_event(self, event):
        """
        Register and show an algorithm event.
        """
        self.last_event = event
        self.event_log.append(event)

        event_html = self.event_as_html(event)
        self.last_event_display.html(event_html)
        self.log_display.append(event_html)

        ajax.get("/graph_data", oncomplete=self.on_new_graph_data)

    def on_new_graph_data(self, req):
        """
        New graph data received, update graph.
        """
        graph_data = jsjson.parse(req.text)["graph_data"]
        render_graph(graph_data.nodes, graph_data.nodes_count, graph_data.max_depth)

    def register_stats(self, stats):
        """
        Register new stats from the algorithm.
        """
        self.stats = stats
        self.stats_display.html("".join(
            f"""<h2>{stat.name}</h2>
                <p>{stat.value}</p>"""
            for stat in stats
        ))

    def event_as_html(self, event):
        """
        Build the html for a single event.
        """
        return f"""<h2>{event.name}</h2>
                   <p>{event.description}</p>"""

    def on_control_algorithm_click(self, e):
        """
        Tell the running algorithm to do something.
        """
        action = e.target.getAttribute("data-action")
        ajax.get(f"/control/{action}")

        in_help = self.current_tab == Tab.HELP
        wants_to_advance = AlgorithmAction(action) in (AlgorithmAction.PLAY, AlgorithmAction.STEP)
        if in_help and wants_to_advance:
            self.switch_to_tab(Tab.GRAPH)

    def on_speed_slider_change(self, e):
        """
        Tell the running algorithm to change speed (setting the interval between events).
        """
        interval = 1.0 / (2 ** int(jq(e.target).val()))
        ajax.get(f"/set_stream_interval/{interval:.10f}")

    def on_show_tab_click(self, e):
        """
        Show a specific tab, defined by the clicked control.
        """
        tab = Tab(e.target.getAttribute("data-tab"))
        self.switch_to_tab(tab)
