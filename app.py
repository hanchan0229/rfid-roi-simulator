import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go

app = dash.Dash(__name__)
app.title = "RFID ROI Simulator"

scenarios = []

app.layout = html.Div([
    html.H1("RFID ROIシミュレーター", style={'textAlign': 'center'}),

    html.Div([
        html.H3("シナリオ入力"),
        html.Div([
            html.Label("RFIDタグ単価（円）"),
            dcc.Input(id='tag_cost', type='number', value=50),

            html.Label("人件費（円/時間）"),
            dcc.Input(id='labor_cost', type='number', value=1500),

            html.Label("導入前作業時間（時間/回）"),
            dcc.Input(id='time_before', type='number', value=1.0),

            html.Label("導入後作業時間（時間/回）"),
            dcc.Input(id='time_after', type='number', value=0.5),

            html.Label("月間作業回数"),
            dcc.Input(id='task_count', type='number', value=100),

            html.Label("1回あたりのタグ使用数"),
            dcc.Input(id='tags_per_task', type='number', value=10),

            html.Label("初期設備費（円）"),
            dcc.Input(id='setup_cost', type='number', value=100000),

            html.Label("月額運用費（円）"),
            dcc.Input(id='maintenance_cost', type='number', value=5000),

            html.Button('シナリオ追加', id='add_scenario', n_clicks=0)
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

        html.Div(id='scenario_list', style={'width': '65%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    html.H3("ROI比較グラフ"),
    dcc.Graph(id='roi_graph')
])

@app.callback(
    Output('scenario_list', 'children'),
    Output('roi_graph', 'figure'),
    Input('add_scenario', 'n_clicks'),
    State('tag_cost', 'value'),
    State('labor_cost', 'value'),
    State('time_before', 'value'),
    State('time_after', 'value'),
    State('task_count', 'value'),
    State('tags_per_task', 'value'),
    State('setup_cost', 'value'),
    State('maintenance_cost', 'value')
)
def update_scenarios(n_clicks, tag_cost, labor_cost, time_before, time_after, task_count, tags_per_task, setup_cost, maintenance_cost):
    if n_clicks > len(scenarios):
        labor_cost_before = labor_cost * time_before * task_count
        labor_cost_after = labor_cost * time_after * task_count
        tag_total_cost = tag_cost * tags_per_task * task_count
        total_cost = setup_cost + maintenance_cost + labor_cost_after + tag_total_cost
        benefit = labor_cost_before - labor_cost_after
        roi = ((benefit - setup_cost - maintenance_cost - tag_total_cost) / (setup_cost + maintenance_cost + tag_total_cost)) * 100 if (setup_cost + maintenance_cost + tag_total_cost) > 0 else 0

        scenario = {
            'name': f'シナリオ {len(scenarios)+1}',
            'ROI': roi,
            '労務費削減': benefit,
            'タグ費用': tag_total_cost,
            '総コスト': total_cost
        }
        scenarios.append(scenario)

    table = html.Table([
        html.Tr([html.Th("シナリオ"), html.Th("ROI（%）"), html.Th("労務費削減（円）"), html.Th("タグ費用（円）"), html.Th("総コスト（円）")])
    ] + [
        html.Tr([html.Td(s['name']), html.Td(f"{s['ROI']:.2f}"), html.Td(f"{s['労務費削減']:.0f}"), html.Td(f"{s['タグ費用']:.0f}"), html.Td(f"{s['総コスト']:.0f}")])
        for s in scenarios
    ])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[s['name'] for s in scenarios],
        y=[s['ROI'] for s in scenarios],
        name='ROI（%）',
        marker_color='green'
    ))
    fig.update_layout(title='シナリオ別ROI比較', xaxis_title='シナリオ', yaxis_title='ROI（%）')

    return table, fig

if __name__ == '__main__':
    app.run_server(debug=True)
