# Bank Marketing Analytics Dashboard
# Libraries: Pandas, NumPy, Plotly, and Dash
import os
import pandas as pd
import numpy as np
import plotly.express as px

from dash import Dash, Input, Output, dcc, html


# --------------------------------------------------
# 1. LOAD AND PREPARE THE DATASET
# --------------------------------------------------

file_name = "bank_market.csv"

if not os.path.exists(file_name):
    raise FileNotFoundError(
        f"'{file_name}' was not found in the current directory. "
        "Please place 'bank_market.csv' in the same folder as this script."
    )

df = pd.read_csv(file_name)

# Make column names consistent.
df.columns = df.columns.str.strip().str.lower()

# Check whether the required columns are available.
required_columns = [
    "age", "job", "marital", "education", "balance", "y"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"The dataset is missing these columns: {missing_columns}"
    )

# Convert age and balance into numbers.
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["balance"] = pd.to_numeric(df["balance"], errors="coerce")

# Clean text values.
text_columns = ["job", "marital", "education", "y"]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .str.lower()
    )

# Remove rows with missing required information.
df = df.dropna(subset=required_columns).copy()

# Keep customers aged 18 and above.
df = df[df["age"] >= 18].copy()

if df.empty:
    raise ValueError(
        "No valid customer records were found in the dataset."
    )

# Create age groups for easier analysis.
age_group_names = [
    "18-25", "26-35", "36-45",
    "46-55", "56-65", "66+"
]

df["age_group"] = pd.cut(
    df["age"],
    bins=[17, 25, 35, 45, 55, 65, np.inf],
    labels=age_group_names
)

print(f"Dataset loaded successfully: {len(df):,} customers")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 2. DASHBOARD COLORS AND SETTINGS
# --------------------------------------------------

BACKGROUND_COLOR = "#F3F6FA"
CARD_COLOR = "#FFFFFF"
PURPLE = "#7650B5"
GREEN = "#16A34A"
ORANGE = "#F97316"
TEXT_COLOR = "#202938"
MUTED_COLOR = "#667085"
GRID_COLOR = "#E5E7EB"

minimum_age = int(df["age"].min())
maximum_age = int(df["age"].max())


# Create dropdown options from the dataset.
def create_dropdown_options(series, all_label):
    values = sorted(series.dropna().astype(str).unique())

    options = [{"label": all_label, "value": "All"}]

    for value in values:
        options.append({
            "label": value.title(),
            "value": value
        })

    return options


job_options = create_dropdown_options(
    df["job"], "All Jobs"
)

marital_options = create_dropdown_options(
    df["marital"], "All Marital Statuses"
)

education_options = create_dropdown_options(
    df["education"], "All Education Levels"
)

subscription_options = create_dropdown_options(
    df["y"], "All Subscriptions"
)

age_group_options = [
    {"label": "All Age Groups", "value": "All"}
]

for group in age_group_names:
    age_group_options.append({
        "label": group,
        "value": group
    })


# --------------------------------------------------
# 3. REUSABLE DASHBOARD COMPONENTS
# --------------------------------------------------

# Common style for filter cards.
filter_style = {
    "backgroundColor": CARD_COLOR,
    "padding": "16px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.05)",
    "flex": "1",
    "minWidth": "180px"
}

# Common style for KPI cards.
kpi_style = {
    "backgroundColor": CARD_COLOR,
    "padding": "22px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.05)",
    "flex": "1",
    "minWidth": "180px"
}

# Common style for chart cards.
chart_style = {
    "backgroundColor": CARD_COLOR,
    "padding": "16px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.05)",
    "minWidth": "0"
}


# Build a filter card.
def create_filter(label, dropdown):
    return html.Div(
        [
            html.Label(
                label,
                style={
                    "fontWeight": "bold",
                    "display": "block",
                    "marginBottom": "10px",
                    "color": TEXT_COLOR
                }
            ),
            dropdown
        ],
        style=filter_style
    )


# Build a KPI card.
def create_kpi_card(label, component_id):
    return html.Div(
        [
            html.P(
                label,
                style={
                    "color": MUTED_COLOR,
                    "margin": "0 0 10px"
                }
            ),
            html.H2(
                id=component_id,
                children="0",
                style={
                    "color": PURPLE,
                    "margin": "0",
                    "fontSize": "30px"
                }
            )
        ],
        style=kpi_style
    )


# Build a chart card.
def create_chart_card(title, component_id):
    return html.Div(
        [
            html.H3(
                title,
                style={
                    "color": TEXT_COLOR,
                    "fontSize": "18px"
                }
            ),
            dcc.Graph(
                id=component_id,
                style={"height": "350px"},
                config={"displayModeBar": True}
            )
        ],
        style=chart_style
    )


# --------------------------------------------------
# 4. CREATE THE DASH APPLICATION
# --------------------------------------------------

app = Dash(__name__)
app.title = "Bank Marketing Analytics Dashboard"


app.layout = html.Div(
    [
        # Dashboard heading.
        html.Div(
            [
                html.H1(
                    "Bank Marketing Analytics Dashboard",
                    style={
                        "textAlign": "center",
                        "color": TEXT_COLOR,
                        "fontSize": "32px",
                        "marginBottom": "8px"
                    }
                ),
                html.P(
                    "Turning customer insights into smarter "
                    "term deposit strategies",
                    style={
                        "textAlign": "center",
                        "color": MUTED_COLOR
                    }
                )
            ],
            style={"marginBottom": "25px"}
        ),

        # Customer filters.
        html.Div(
            [
                create_filter(
                    "Job",
                    dcc.Dropdown(
                        id="job-filter",
                        options=job_options,
                        value="All",
                        clearable=False
                    )
                ),

                create_filter(
                    "Marital Status",
                    dcc.Dropdown(
                        id="marital-filter",
                        options=marital_options,
                        value="All",
                        clearable=False
                    )
                ),

                create_filter(
                    "Education",
                    dcc.Dropdown(
                        id="education-filter",
                        options=education_options,
                        value="All",
                        clearable=False
                    )
                ),

                create_filter(
                    "Subscription",
                    dcc.Dropdown(
                        id="subscription-filter",
                        options=subscription_options,
                        value="All",
                        clearable=False
                    )
                ),

                create_filter(
                    "Age Group",
                    dcc.Dropdown(
                        id="age-group-filter",
                        options=age_group_options,
                        value="All",
                        clearable=False
                    )
                )
            ],
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "16px",
                "marginBottom": "22px"
            }
        ),

        # Age range filter.
        html.Div(
            [
                html.Label(
                    "Customer Age Range",
                    style={
                        "fontWeight": "bold",
                        "fontSize": "18px",
                        "color": TEXT_COLOR
                    }
                ),

                dcc.RangeSlider(
                    id="age-range-filter",
                    min=minimum_age,
                    max=maximum_age,
                    value=[minimum_age, maximum_age],
                    marks={
                        age: str(age)
                        for age in sorted(
                            set(
                                [minimum_age, maximum_age]
                                + list(
                                    range(
                                        ((minimum_age + 9) // 10) * 10,
                                        maximum_age,
                                        10
                                    )
                                )
                            )
                        )
                    },
                    step=1,
                    allowCross=False,
                    tooltip={
                        "placement": "bottom",
                        "always_visible": False
                    },
                    updatemode="mouseup"
                )
            ],
            style={
                "backgroundColor": CARD_COLOR,
                "padding": "25px 25px 38px",
                "borderRadius": "12px",
                "marginBottom": "22px",
                "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.05)"
            }
        ),

        # KPI cards.
        html.Div(
            [
                create_kpi_card(
                    "Total Customers", "total-customers"
                ),
                create_kpi_card(
                    "Average Balance", "average-balance"
                ),
                create_kpi_card(
                    "Subscribers", "total-subscribers"
                )
            ],
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "16px",
                "marginBottom": "22px"
            }
        ),

        # Interactive charts.
        html.Div(
            [
                create_chart_card(
                    "Age Distribution", "age-chart"
                ),
                create_chart_card(
                    "Customer Jobs", "job-chart"
                ),
                create_chart_card(
                    "Balance vs Age", "scatter-chart"
                ),
                create_chart_card(
                    "Subscription Status", "subscription-chart"
                )
            ],
            style={
                "display": "grid",
                "gridTemplateColumns":
                    "repeat(auto-fit, minmax(300px, 1fr))",
                "gap": "18px"
            }
        ),

        # Dashboard footer.
        html.P(
            "Built with Python, Pandas, NumPy, Dash and Plotly",
            style={
                "textAlign": "center",
                "color": MUTED_COLOR,
                "marginTop": "25px"
            }
        )
    ],
    style={
        "backgroundColor": BACKGROUND_COLOR,
        "minHeight": "100vh",
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
        "color": TEXT_COLOR
    }
)


# --------------------------------------------------
# 5. FILTER DATA AND UPDATE THE DASHBOARD
# --------------------------------------------------

@app.callback(
    [
        Output("total-customers", "children"),
        Output("average-balance", "children"),
        Output("total-subscribers", "children"),
        Output("age-chart", "figure"),
        Output("job-chart", "figure"),
        Output("scatter-chart", "figure"),
        Output("subscription-chart", "figure")
    ],
    [
        Input("job-filter", "value"),
        Input("marital-filter", "value"),
        Input("education-filter", "value"),
        Input("subscription-filter", "value"),
        Input("age-group-filter", "value"),
        Input("age-range-filter", "value")
    ]
)
def update_dashboard(
    selected_job,
    selected_marital,
    selected_education,
    selected_subscription,
    selected_age_group,
    selected_age_range
):
    # Start with the complete dataset.
    filtered_data = df.copy()

    # Apply the selected job filter.
    if selected_job != "All":
        filtered_data = filtered_data[
            filtered_data["job"] == selected_job
        ]

    # Apply the marital status filter.
    if selected_marital != "All":
        filtered_data = filtered_data[
            filtered_data["marital"] == selected_marital
        ]

    # Apply the education filter.
    if selected_education != "All":
        filtered_data = filtered_data[
            filtered_data["education"] == selected_education
        ]

    # Apply the subscription filter.
    if selected_subscription != "All":
        filtered_data = filtered_data[
            filtered_data["y"] == selected_subscription
        ]

    # Apply the age group filter.
    if selected_age_group != "All":
        filtered_data = filtered_data[
            filtered_data["age_group"].astype("string")
            == selected_age_group
        ]

    # Apply the minimum and maximum age.
    if selected_age_range:
        minimum_selected_age, maximum_selected_age = selected_age_range

        filtered_data = filtered_data[
            filtered_data["age"].between(
                minimum_selected_age,
                maximum_selected_age
            )
        ]

    # Calculate the KPI values.
    total_customers = len(filtered_data)

    if total_customers > 0:
        average_balance = filtered_data["balance"].mean()
        subscribers = int(
            (filtered_data["y"] == "yes").sum()
        )
    else:
        average_balance = 0
        subscribers = 0

    # Apply the same style to every chart.
    def style_chart(figure):
        figure.update_layout(
            template="plotly_white",
            margin=dict(l=25, r=20, t=20, b=45),
            font=dict(family="Arial", color=TEXT_COLOR),
            paper_bgcolor=CARD_COLOR,
            plot_bgcolor=CARD_COLOR
        )

        figure.update_xaxes(gridcolor=GRID_COLOR)
        figure.update_yaxes(gridcolor=GRID_COLOR)

        return figure

    # Chart 1: Age distribution.
    age_figure = px.histogram(
        filtered_data,
        x="age",
        nbins=20,
        labels={
            "age": "Customer Age",
            "count": "Customers"
        },
        color_discrete_sequence=[PURPLE]
    )

    age_figure.update_layout(
        xaxis_title="Customer Age",
        yaxis_title="Number of Customers",
        bargap=0.08
    )

    style_chart(age_figure)

    # Chart 2: Number of customers in each job.
    job_counts = (
        filtered_data["job"]
        .value_counts()
        .rename_axis("job")
        .reset_index(name="customers")
        .sort_values("customers", ascending=True)
    )

    job_figure = px.bar(
        job_counts,
        x="customers",
        y="job",
        orientation="h",
        labels={
            "job": "Job",
            "customers": "Customers"
        },
        color_discrete_sequence=[PURPLE]
    )

    job_figure.update_layout(
        xaxis_title="Number of Customers",
        yaxis_title="",
        yaxis={"automargin": True}
    )

    style_chart(job_figure)

    # Chart 3: Relationship between age and account balance.
    scatter_data = filtered_data

    if len(scatter_data) > 3000:
        scatter_data = scatter_data.sample(
            n=3000,
            random_state=42
        )

    scatter_figure = px.scatter(
        scatter_data,
        x="age",
        y="balance",
        color="y",
        hover_data=["job", "marital", "education"],
        labels={
            "age": "Customer Age",
            "balance": "Account Balance",
            "y": "Subscribed"
        },
        color_discrete_map={
            "yes": GREEN,
            "no": ORANGE
        },
        opacity=0.65
    )

    scatter_figure.update_layout(
        xaxis_title="Customer Age",
        yaxis_title="Account Balance"
    )

    style_chart(scatter_figure)

    # Chart 4: Subscription status.
    subscription_counts = (
        filtered_data["y"]
        .value_counts()
        .rename_axis("subscription")
        .reset_index(name="customers")
    )

    subscription_figure = px.pie(
        subscription_counts,
        names="subscription",
        values="customers",
        hole=0.4,
        color="subscription",
        color_discrete_map={
            "yes": GREEN,
            "no": ORANGE
        },
        labels={
            "subscription": "Subscription",
            "customers": "Customers"
        }
    )

    subscription_figure.update_traces(
        textposition="inside",
        textinfo="label+percent"
    )

    style_chart(subscription_figure)

    # Show a message on the charts if no records match the filters.
    if filtered_data.empty:
        empty_message = "No customers match the selected filters."

        for figure in [
            age_figure,
            job_figure,
            scatter_figure,
            subscription_figure
        ]:
            figure.add_annotation(
                text=empty_message,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font={"size": 14, "color": MUTED_COLOR}
            )

    # Send updated KPI values and charts to the dashboard.
    return (
        f"{total_customers:,}",
        f"{average_balance:,.2f}",
        f"{subscribers:,}",
        age_figure,
        job_figure,
        scatter_figure,
        subscription_figure
    )


# --------------------------------------------------
# 6. RUN THE DASHBOARD LOCALLY IN VS CODE
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        port=8050
    )