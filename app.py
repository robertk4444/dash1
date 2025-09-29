
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from io import StringIO
import os

# --- Osadzone dane CSV (demo) ---
csv_data = """
TransactionID,Date,Time,TableID,Product,Quantity,UnitPrice,FinalPrice,Cost,PaymentMethod,Total
1,2025-09-06,09:42:36,1,Sałatka grecka,2,25,50.0,9,Gotówka,50.0
2,2025-09-05,23:24:55,18,Pizza Pepperoni,4,34,136.0,10,Gotówka,136.0
3,2025-09-05,13:09:46,7,Stek wołowy,1,78,70.2,30,Gotówka,70.2
4,2025-09-21,08:46:33,8,Piwo 0.5l,3,15,45.0,5,Gotówka,45.0
5,2025-09-21,12:22:53,11,Sałatka grecka,2,25,50.0,9,Karta,50.0
6,2025-09-12,18:44:34,5,Kawa latte,1,15,13.5,3,Karta,13.5
7,2025-09-19,17:17:11,12,Burger klasyczny,2,38,76.0,15,Gotówka,76.0
8,2025-09-26,21:13:50,9,Pizza Margherita,3,29,87.0,12,Karta,87.0
9,2025-09-10,15:01:25,4,Piwo 0.5l,4,15,60.0,5,Karta,60.0
10,2025-09-15,11:30:00,6,Kawa czarna,2,10,20.0,2,Karta,20.0
""".strip()

df = pd.read_csv(StringIO(csv_data))

# Przygotowanie danych
df["Date"] = pd.to_datetime(df["Date"])
df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
df["Weekday"] = df["Date"].dt.day_name()

# Aplikacja Dash
app = dash.Dash(__name__)
server = app.server  # dla Render

app.layout = html.Div([
    html.H1("📊 Dashboard sprzedaży POS"),
    
    html.Label("Metoda płatności"),
    dcc.Dropdown(
        id="payment-filter",
        options=[{"label": pm, "value": pm} for pm in sorted(df["PaymentMethod"].dropna().unique())],
        multi=True
    ),
    
    dcc.Graph(id="line-chart"),
    dcc.Graph(id="heatmap"),
    dcc.Graph(id="top-products")
])

@app.callback(
    Output("line-chart", "figure"),
    Output("heatmap", "figure"),
    Output("top-products", "figure"),
    Input("payment-filter", "value")
)
def update_charts(payment_methods):
    dff = df.copy()
    if payment_methods:
        dff = dff[dff["PaymentMethod"].isin(payment_methods)]

    # Wykres 1: Sprzedaż godzinowa wg dnia tygodnia
    hourly = dff.groupby(["Weekday", "Hour"])["Total"].sum().reset_index()
    hourly["Weekday"] = pd.Categorical(
        hourly["Weekday"],
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        ordered=True
    )
    fig1 = px.line(hourly, x="Hour", y="Total", color="Weekday", title="Sprzedaż wg godziny i dnia tygodnia")

    # Wykres 2: Heatmapa
    heatmap_df = dff.pivot_table(index="Weekday", columns="Hour", values="Total", aggfunc="sum", fill_value=0)
    heatmap_df = heatmap_df.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    fig2 = px.imshow(heatmap_df, labels=dict(x="Godzina", y="Dzień tygodnia", color="Sprzedaż"),
                     title="Heatmapa sprzedaży")

    # Wykres 3: Top produkty
    top_products = dff.groupby("Product")["Total"].sum().sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(top_products, x="Total", y="Product", orientation="h", title="Top 10 produktów")

    return fig1, fig2, fig3

if __name__ == "__main__":
    # Kluczowe dla Render: użyj portu z env i nasłuchuj na 0.0.0.0
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
