
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go

app = dash.Dash(__name__)
app.title = "RFID ROIシミュレーター（累積キャッシュフロー対応）"

scenarios = []

app.layout = html.Div([
    html.H1("RFID ROIシミュレーター", style={'textAlign': 'center'}),

    html.Div([
        html.H3("シナリオ入力"),
        html.Div([
            html.Label("RFIDタグ単価（円）"),
            dcc.Input(id='tag_cost', type='number', value=50, style={'width': '100%'}),

            html.Label("人件費（円/時間）"),
            dcc.Input(id='labor_cost', type='number', value=1500, style={'width': '100%'}),

            html.Label("導入前作業時間（時間/回）"),
            dcc.Input(id='time_before', type='number', value=1.0, style={'width': '100%'}),

            html.Label("導入後作業時間（時間/回）"),
            dcc.Input(id='time_after', type='number', value=0.5, style={'width': '100%'}),

            html.Label("月間作業回数"),
            dcc.Input(id='task_count', type='number', value=100, style={'width': '100%'}),

            html.Label("1回あたりのタグ使用数"),
            dcc.Input(id='tags_per_task', type='number', value=10, style={'width': '100%'}),

            html.Label("初期設備費（円）"),
            dcc.Input(id='setup_cost', type='number', value=100000, style={'width': '100%'}),

            html.Label("月額運用費（円）"),
            dcc.Input(id='maintenance_cost', type='number', value=5000, style={'width': '100%'}),

            html.Button('シナリオ追加', id='add_scenario', n_clicks=0, style={'marginTop': '10px'})
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

        html.Div(id='scenario_list', style={'width': '65%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    html.H3("累積キャッシュフロー（24ヶ月）"),
    dcc.Graph(id='cashflow_graph')
])

@app.callback(
    Output('scenario_list', 'children'),
    Output('cashflow_graph', 'figure'),
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
        monthly_saving = labor_cost_before - labor_cost_after
        monthly_cost = maintenance_cost + tag_total_cost
        initial_investment = setup_cost + monthly_cost
        cumulative_cashflow = [-setup_cost]
        for month in range(1, 25):
            net = monthly_saving - monthly_cost
            cumulative_cashflow.append(cumulative_cashflow[-1] + net)

        scenario = {
            'name': f'シナリオ {len(scenarios)+1}',
            'monthly_saving': monthly_saving,
            'monthly_cost': monthly_cost,
            'initial_investment': setup_cost,
            'cumulative_cashflow': cumulative_cashflow[1:]
        }
        scenarios.append(scenario)

    table = html.Table([
        html.Tr([html.Th("シナリオ"), html.Th("月間削減額（円）"), html.Th("月間コスト（円）"), html.Th("初期投資（円）")])
    ] + [
        html.Tr([html.Td(s['name']), html.Td(f"{s['monthly_saving']:.0f}"), html.Td(f"{s['monthly_cost']:.0f}"), html.Td(f"{s['initial_investment']:.0f}")])
        for s in scenarios
    ])

    fig = go.Figure()
    for s in scenarios:
        fig.add_trace(go.Scatter(
            x=list(range(1, 25)),
            y=s['cumulative_cashflow'],
            mode='lines+markers',
            name=s['name']
        ))
    fig.update_layout(title='累積キャッシュフロー（24ヶ月）', xaxis_title='月', yaxis_title='累積キャッシュフロー（円）')

    return table, fig

if __name__ == '__main__':
    app.run_server(debug=True)
