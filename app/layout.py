from dash import dcc, html
import dash_bootstrap_components as dbc


def get_layout():
    """
    Returns the main layout structure for the
    Intelligent Device Health Monitoring System.
    """

    return dbc.Container([

        # =========================
        # Header
        # =========================
        html.H1(
            "Intelligent Device Health Monitoring System",
            className="text-center my-4 text-primary"
        ),

        html.Hr(),

        # =========================
        # Auto Refresh
        # =========================
        dcc.Interval(
            id='interval-component',
            interval=30 * 1000,  # 30 seconds
            n_intervals=0
        ),

        # =========================
        # Tabs Navigation
        # =========================
        dcc.Tabs(
            id="tabs",
            value='tab-overview',
            className="mb-4",
            children=[

                dcc.Tab(
                    label='Overview',
                    value='tab-overview',
                    children=[]
                ),

                dcc.Tab(
                    label='Anomalies',
                    value='tab-anomalies',
                    children=[]
                ),

                dcc.Tab(
                    label='Alerts',
                    value='tab-alerts',
                    children=[]
                ),

                dcc.Tab(
                    label='Logs',
                    value='tab-logs',
                    children=[]
                ),
            ]
        ),

        # =========================
        # Dynamic Tab Content
        # =========================
        html.Div(
            id='tabs-content',
            className="mt-3"
        ),

    ], fluid=True)