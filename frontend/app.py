from plotly import graph_objects as go
import dash
from dash import html, dcc, Input, Output, State
import datetime
import httpx
import io
from PIL import Image
import pandas as pd
from dash import dcc
from pathlib import Path
import numpy as np
import json
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from rag_engine import get_results


# df = pd.read_csv('data/local/hun_sum_portfolio.csv')
# df = df[~df['date_of_creation'].isna()]
# df['timestamp'] = df['date_of_creation'].map(lambda x: int(datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp()))


df = pd.read_csv('data/local/hun_sum_portfolio.csv').set_index('uuid')
df = df[['title', 'domain', 'url', 'date_of_creation', 'tags']]
df['day'] = pd.to_datetime(df['date_of_creation']).dt.floor('D')

retriever = None



def pull_articles(start_date, end_date):
    filtered_df = df[(pd.Timestamp(start_date) <= df['day']) & (df['day'] <= pd.Timestamp(end_date) )]
    relevant_articles = filtered_df.sample(min(500, len(filtered_df)))
    return relevant_articles


local_timezone = ZoneInfo('Europe/Budapest')

def render_content(articles: pd.DataFrame) -> html.Div:
    count_by_day = articles.groupby('day').size().reset_index(name='count')

    article_count_fig = go.Figure(
        go.Bar(
            x=count_by_day['day'],
            y=count_by_day['count'],
            marker_color='blue'
        ),
        layout=go.Layout(
            title="Article Frequency",
            xaxis_title="Date",
            yaxis_title="Number of Articles",
            width=1200,
            height=800,
            # margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )
    )
    
    article_cards = []
    for article in articles.to_dict(orient='records'):

        domain = article['domain']
        domain_img = f"/assets/domains/{domain}.svg"

        time_str = article['date_of_creation']
        article_cards.append(
            html.Div(
                [html.A(
                    html.Div(
                        [
                            html.Div(className="timestamp", children=time_str),
                            html.Div(
                                [
                                    html.Img(src=domain_img, style={
                                        "alignSelf": "left",
                                        "maxWidth": "60px",
                                        "maxHeight": "60px",
                                        "display": "inline-block"
                                    }),
                                    html.Div(
                                        className="text",
                                        children=article["title"],
                                        style={
                                            "alignSelf": "left",
                                            "wordWrap": "break-word",
                                            "overflowWrap": "break-word",
                                            "whiteSpace": "normal",
                                            "flex": "1",
                                            "backgroundColor": "#f899fa",
                                            "display": "inline-block",
                                            "maxHeight": "100px",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "flex-start",
                                    "justifyContent": "flex-start",
                                    "flexDirection": "column",
                                    "borderRadius": "6px",
                                    "boxSizing": "border-box",
                                    "textAlign": "left",
                                    "width": "100%",
                                    "backgroundColor": "#f899fa",
                                    "maxHeight": "100px",
                                },
                                className="card-body",
                            )
                        ],

                    ),
                    href=article["url"],
                    target="_blank",
                    className="card-link",
                ),
            ],
            style={"width": "100%", "margin-left": "10px",}
            )
        )

    return html.Div(
        html.Div(
            [
                html.Div(
                    [dcc.Graph(figure=article_count_fig, config={"responsive": True}, style={
                        "width": "100%",
                        "height": "100%",
                        "margin": "0 auto",
                    })],
                    style={
                        "justifyContent": "center",
                        "alignItems": "center",
                        "flex": "0 0 80%",
                        "boxSizing": "border-box"
                    }
                ),
                html.Div(
                    children=article_cards,
                    style={
                        "flex": "0 0 20%",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "height": "800px",         # or any fixed height you prefer
                        "overflowY": "auto",       # enables vertical scrolling
                        "paddingRight": "10px",    # avoid scrollbar overlap
                        "border": "1px solid #ccc",
                        "borderRadius": "6px"
                    }
                )
            ],
            style={"display": "flex", "flexDirection": "row", "width": "100%", "alignContent": "center", "justifyContent": "center", "gap": "10px"},
        ),
    )


layout = html.Div(
    [
        dcc.Store(id="retriever", data={"value": None}),
        html.H1("RAGtime"),
        
        html.Div(
            [
                dcc.Input(id="prompt-input", type="text", placeholder="Enter your prompt...", style={"width": "100%"}),
                html.Br(),

                html.Div(
                    [
                        html.Label("Region"),
                        dcc.Dropdown(
                            id="region-selector",
                            options=[
                                {"label": "North America", "value": "na"},
                                {"label": "Europe", "value": "eu"},
                                {"label": "Asia", "value": "asia"},
                                {"label": "Global", "value": "global"},
                            ],
                            value="global",
                            style={"width": "50%"},
                            clearable=False
                        ),
                    ],
                    style={"marginBottom": "15px"}
                ),

                html.Div(
                    [
                        html.Label("Start Date"),
                        dcc.DatePickerSingle(
                            id="start-date",
                            date='2005-01-01',
                            # date=(datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
                        ),
                        html.Label("End Date", style={"marginLeft": "20px"}),
                        dcc.DatePickerSingle(
                            id="end-date",
                            date='2025-05-30',
                            # date=datetime.now().strftime('%Y-%m-%d')
                        ),
                    ],
                    style={"marginBottom": "15px"}
                ),

                html.Br(),
                html.Button("Search", id="submit-button", n_clicks=0)
            ],
            className="search-container",
        ),
        html.Hr(),
        html.Div(id="timeline-container", className='timeline-container')
    ],
    id="root-container"
)


app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Article Timeline Explorer"
app.layout = layout

@app.callback(
    Output("timeline-container", "children"),
    Input("submit-button", "n_clicks"),
    State("prompt-input", "value"),
    State("region-selector", "value"),
    State("start-date", "date"),
    State("end-date", "date"),
    State("retriever", "data"),
)
def update_timeline(
    n_clicks,
    prompt,
    region,
    start_date,
    end_date,
    stored_retriever,
):
    if not n_clicks:
        return []

    results, stored_retriever['value'] = get_results(prompt, stored_retriever['value'])

    relevant_articles = df.loc[[a['node']['id_'] for a in results]]
    relevant_articles['score'] = [a['score'] for a in results]
    relevant_articles = relevant_articles.sort_values(by='score', ascending=False)

    relevant_articles = relevant_articles[
        (pd.Timestamp(start_date) <= relevant_articles['day']) & (relevant_articles['day'] <= pd.Timestamp(end_date))
    ]

    content = render_content(relevant_articles)

    return content


if __name__ == "__main__":
    app.run(debug=True)