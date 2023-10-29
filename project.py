import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 读取数据集
data = pd.read_csv('home/warehouse_master_dataset.csv', parse_dates=['Date'], dayfirst=True)  # 替换为你的数据文件路径
data['Date'] = pd.to_datetime(data['Date'])
data['week'] = data['Date'].dt.isocalendar().week 

unique_weeks = list(data.week.unique())
unique_weeks.sort()
option_weeks = list()
for week in unique_weeks:
    option_weeks.append("Week "+str(week))

app = dash.Dash(__name__)

def leftDiv():
    return   html.Div(style={'width': '300px'}, children=[
        dcc.Dropdown(
        id='week-filter',
        options= option_weeks,
        clearable = False,
        style={
            'width': '300px',            
            'height': '40px',          
        },
        value=option_weeks[0]
        ),

        html.Div( className="item-content",children=[
            html.Span(id='text-1',className="item-text-font1 color-blue", children='$'),
            html.Span(id='text-revenue',className="item-text-font2 color-blue", children='5000'),
            html.Span(id='text-3',className="item-text-font1 color-blue", children='k'),
            html.Br(),
            html.Span(id='text-4',className="item-text-font3", children='Weekly Revenue'),
            html.Br(),
            html.Span(id='text-revenue-last',className="item-text-font4", children='+ $50.4k vs last week'),
        ]),

        html.Div( className="item-content",children=[
            html.Span(id='text-orders',className="item-text-font2 color-blue", children='5383'),
            html.Br(),
            html.Span(id='text-5',className="item-text-font3", children='Orders'),
            html.Br(),
            html.Span(id='text-orders-last',className="item-text-font4", children='+ 598 vs last week'),
        ]),
    
        html.Div( className="item-content",children=[
            html.Span(id='text-6',className="item-text-font5", children='inventory Turnover Rate'),
            html.Br(),
            html.Span(id='text-inventory',className="item-text-font2 color-blue", children='8'),
            
        ])
    ])

def middleDiv():
    return html.Div(style={'flex': '1' ,'margin': '0 10px','height': '420px'},children=[
        html.Div(style={"background-color":"white"},children=[
            dcc.RadioItems(
                id='midTopOptions',
                options=[
                    {'label': 'Television', 'value': 'Television'},
                    {'label': 'Air Conditioner', 'value': 'AirConditioner'},
                    {'label': 'Refrigerator', 'value': 'Refrigerator'},
                    {'label': 'Washing Machine', 'value': 'WashingMachine'}
                ],
                 inline=True,
                value='Television',
            ),
            dcc.Graph(
                style={'height': '400px','margin-top':"0px"} ,
                id='midTopGraph'
            )
        ]),
        html.Div(style={"background-color":"white","margin-top":"10px",'height': '400px'},children=[
            dcc.Graph(
                style={"background-color":"white","margin-top":"10px",'height': '400px'},
                id='line-chart'
                ),
        ]),
        html.Div(style={"background-color":"white","margin-top":"10px",'height': '180px','display': 'flex'},children=[
            html.Div(className="item-content", style={'flex': '1'},children=[
                html.Span(id='return_order_text', className="item-text-font5", children='Return'),
                html.Br(),
                html.Span(id='return_order', className="item-text-font2 color-blue", children='8'),
                html.Br(),
                html.Span(id='orders_text', className="item-text-font3", children='Orders'),
            ]),
            html.Div(className="item-content", style={'flex': '1'},children=[
                html.Span(id='return_rate_text', className="item-text-font5", children='Return rate'),
                html.Br(),
                html.Span(id='return_rate', className="item-text-font2 color-blue", children='8'),
            ])
        ])
    ])

def rightDiv():
    return html.Div(style={'width':'320px'}, children=[
        html.Div(style={"background-color":"white",'height':'420px'},children=[
            dcc.Graph(
                style={"background-color":"white",'height':'420px'},
                id='utilization_chart'
                )
        ]),
        html.Div(style={"background-color":"white","margin-top":"10px",'height':'400px'},children=[
            dcc.Graph(
                style={"background-color":"white","margin-top":"10px",'height':'400px'},
                id='pieGraph'
            )
        ])
    ])

app.layout = html.Div([
    html.H1("WAREHOUSE OPERATIONS DASHBOARD"),
    html.Div(style={'display': 'flex'},  children = [
        leftDiv(),
        middleDiv(),
        rightDiv()
    ])
])

@app.callback(
    [Output('text-orders', 'children'),
     Output('text-orders-last', 'children'),
     Output('text-revenue', 'children'),
     Output('text-revenue-last', 'children'),
     Output('text-inventory', 'children'),],
    Input('week-filter', 'value')
)
def update_week_data(week:str):
    week_num = int(week.replace("Week ",""))
    week_df = data[data.week == week_num]

    week_order = week_df["Order_Quantity"].sum()
    last_sub_week_order = 0

    week_revenue = week_df["Daily_Revenue"].sum()
    last_sub_week_revenue = 0

    inventory_rate = int(week_df["Inventory_Turnover"].sum() / len(week_df))

    if week_num > 1:
        last_week_df = data[data.week == (week_num-1)]

        last_week_order = last_week_df["Order_Quantity"].sum()
        last_sub_week_order = week_order - last_week_order

        last_week_revenue = last_week_df["Daily_Revenue"].sum()
        last_sub_week_revenue = week_revenue - last_week_revenue

    char_order = "+" if last_sub_week_order >= 0 else "-"
    char_revenue = "+" if last_sub_week_revenue >= 0 else "-"

    return [str(week_order),
            f"{char_order} {abs(last_sub_week_order)} vs last week",
            str(week_revenue),
            f"{char_revenue} {abs(last_sub_week_revenue)} vs last week",
            str(inventory_rate)
            ]



@app.callback(
    Output('midTopGraph', 'figure'),
    [Input('week-filter', 'value'),
     Input('midTopOptions', 'value')]
)
def update_graph(selected_week, item_name):
    week_num = int(selected_week.replace("Week ",""))
    selected_data = data[data.week == week_num]
    fig = px.bar(selected_data, x='Date', y=item_name, title=f'Order Quantity')
    fig.update_yaxes(title_text=None)
    fig.update_layout(margin=dict(l=0))
    fig.update_xaxes(title_text=None,tickvals =selected_data['Date'], tickmode='array',ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fn', 'Sat', 'Sun'])
    return fig

@app.callback(
    Output('line-chart', 'figure'),
    Input('week-filter', 'value')
)
def update_line_chart(selected_week):
    # Filter data based on the selected week
    week_num = int(selected_week.replace("Week ",""))
    filtered_data = data[data.week == week_num]
    
    # Create a line chart for Picking Accuracy
    fig = px.line(filtered_data, x='Date', y='Picking_Accuracy', title=f'Picking Accuracy')
    fig.update_layout(margin=dict(l=0))
    fig.update_yaxes(title_text=None, range=[0.9, 1], tickvals=[0.90, 0.92, 0.94, 0.96,0.98, 1], tickformat=".2%")
    fig.update_xaxes(title_text=None,tickvals =filtered_data['Date'], tickmode='array',ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fn', 'Sat', 'Sun'])
    return fig

@app.callback(
    Output('utilization_chart', 'figure'),
    [Input('week-filter', 'value')]
)
def update_graph(selected_week):
    week_num = int(selected_week.replace("Week ",""))
    selected_data = data[data.week == week_num]
    
    average_utilization = selected_data['Warehouse_Utilization'].mean() * 100  
    
    # Create a doughnut chart using plotly.express
    fig = px.pie(values=[average_utilization, 100-average_utilization], 
                 names=['Utilization', 'Unused'],
                 hole=0.4,  # Set the size of the hole in the middle of the doughnut chart
                 title=f'Warehouse Utilization')

    fig.update_traces(marker=dict(colors=['#000080', '#C0D9B2']),textinfo='percent+label')
    fig.update_layout(showlegend=False)
    return fig

@app.callback(
    Output('pieGraph', 'figure'),
    [Input('week-filter', 'value')]
)
def update_graph(selected_week):
    week_num = int(selected_week.replace("Week ",""))
    selected_data = data[data.week == week_num]

    total_sum = selected_data[['Television', 'AirConditioner', 'Refrigerator', 'WashingMachine']].sum()
    percentage = total_sum / total_sum.sum() * 100

    fig = px.pie(values=percentage, 
                 names=['Television', 'AirConditioner', 'Refrigerator', 'WashingMachine'],
                 title=f'Warehouse Utilization')
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition="inside",textinfo='percent+label')

    return fig 

@app.callback(
    Output('return_order', 'children'),
    Output('return_rate', 'children'),
    [Input('week-filter', 'value')]
)
def update_metrics(selected_week):
    week_num = int(selected_week.replace("Week ",""))
    selected_data = data[data.week == week_num]
    return_order_sum = selected_data['Return_Quantity'].sum()
    return_rate_avg = selected_data['Return_Rate'].mean()
    formatted_return_rate = '{:.2f}%'.format(return_rate_avg * 100)
    return return_order_sum, formatted_return_rate

if __name__ == '__main__':
    app.run_server(debug=True)