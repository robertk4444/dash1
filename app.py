import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# ===== Konfiguracja ścieżki CSV (plik w repo, obok app.py) =====
CSV_PATH = "sprzedaz_pos_100.csv"

# ===== Wczytanie danych z różnymi kodowaniami (PL nagłówki) =====
def load_data():
    encodings = ["utf-8", "utf-8-sig", "cp1250"]
    last_err = None
    for enc in encodings:
        try:
            return pd.read_csv(CSV_PATH, encoding=enc)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Nie można wczytać {CSV_PATH}. Ostatni błąd: {last_err}")

df_raw = load_data()

# ===== Mapowanie nazw kolumn PL -> EN (dopasowane do Twojego CSV) =====
rename_map = {
    "ID transakcji": "TransactionID",
    "Data": "Date",
    "Godzina": "Time",
    "ID stolika": "TableID",
    "Nazwa produktu": "Product",
    "Ilość": "Quantity",
    "Cena jednostkowa brutto": "UnitPrice",
    "Cena końcowa (po rabacie)": "FinalPrice",
    "Koszt własny (food cost)": "Cost",
    "Metoda płatności": "PaymentMethod",
    "Łączna wartość transakcji": "Total",
}
df = df_raw.rename(columns=rename_map).copy()

# ===== Przygotowanie pól czasowych =====
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S", errors="coerce").dt.hour
df["Weekday"] = df["Date"].dt.day_name()
df = df.dropna(subset=["Date", "Hour", "Weekday"])

WEEK_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ===== Aplikacja Dash =====
app = dash.Dash(__name__)
server = app.server  # wymagane przez Render

app.layout = html.Div([
    html.H1("📊 Dashboard sprzedaży POS", style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label("Metoda płatności"),
            dcc.Dropdown(
                id="payment-filter",
                options=[{"label": pm, "value": pm} for pm in sorted(df["PaymentMethod"].dropna().unique())],
                multi=True,
                placeholder="Wybierz metodę (opcjonalnie)"
            ),
        ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "paddingRight": "12px"}),

        html.Div([
            html.Label("Produkt"),
            dcc.Dropdown(
                id="product-filter",
                options=[{"label": p, "value": p} for p in sorted(df["Product"].dropna().unique())],
                multi=True,
                placeholder="Wybierz produkt (opcjonalnie)"
            ),
        ], style={"width": "40%", "display": "inline-block", "verticalAlign": "top", "paddingRight": "12px"}),

        html.Div([
            html.Label("Dzień tygodnia"),
            dcc.Dropdown(
                id="weekday-filter",
                options=[{"label": w, "value": w} for w in WEEK_ORDER],
                value=None,          # domyślnie wszystkie
                multi=True,
                placeholder="Wybierz dni (opcjonalnie)"
            ),
        ], style={"width": "28%", "display": "inline-block", "verticalAlign": "top"}),
    ], style={"marginBottom": "12px"}),

    dcc.Graph(id="line-chart"),             # 1) linie wg dnia tygodnia
    dcc.Graph(id="stacked-line-chart"),     # 2) SUMA godzinowa po wybranych filtrach (w tym dniach)
    dcc.Graph(id="heatmap"),
    dcc.Graph(id="top-products")
])

@app.callback(
    [
        Output("line-chart", "figure"),
        Output("stacked-line-chart", "figure"),
        Output("heatmap", "figure"),
        Output("top-products", "figure"),
    ],
    [
        Input("payment-filter", "value"),
        Input("product-filter", "value"),
        Input("weekday-filter", "value"),
    ]
)
def update_charts(payment_methods, products, weekdays):
    dff = df.copy()

    # Filtrowanie metod płatności i produktów
    if payment_methods:
        dff = dff[dff["PaymentMethod"].isin(payment_methods)]
    if products:
        dff = dff[dff["Product"].isin(products)]

    # Filtrowanie dni tygodnia (jeśli coś zaznaczono)
    if weekdays and len(weekdays) > 0:
        dff = dff[dff["Weekday"].isin(weekdays)]

    # --- 1) Wykres: sprzedaż godzinowa wg dnia tygodnia ---
    hourly = (
        dff.groupby(["Weekday", "Hour"], dropna=False)["Total"]
        .sum().reset_index()
    )
    hourly["Weekday"] = pd.Categorical(hourly["Weekday"], categories=WEEK_ORDER, ordered=True)
    hourly = hourly.sort_values(["Weekday", "Hour"])
    fig1 = px.line(
        hourly, x="Hour", y="Total", color="Weekday",
        title="Sprzedaż wg godziny i dnia tygodnia"
    )

    # --- 2) NOWY Wykres: sprzedaż godzinowa SUMARYCZNA (suma po wybranych filtrach) ---
    hourly_sum = (
        dff.groupby("Hour")["Total"]
        .sum()
        .reindex(range(24), fill_value=0)   # pełne godziny 0..23
        .reset_index().rename(columns={"index": "Hour"})
        .sort_values("Hour")
    )
    fig_sum = px.line(
        hourly_sum, x="Hour", y="Total",
        title="Sprzedaż wg godziny (suma wybranych filtrów)"
    )

    # --- 3) Heatmapa ---
    heatmap = (
        dff.pivot_table(index="Weekday", columns="Hour", values="Total", aggfunc="sum", fill_value=0)
        .reindex(WEEK_ORDER)
    )
    fig2 = px.imshow(
        heatmap,
        labels=dict(x="Godzina", y="Dzień tygodnia", color="Sprzedaż"),
        title="Heatmapa: dzień tygodnia vs godzina"
    )

    # --- 4) Top produkty ---
    top_products = (
        dff.groupby("Product", drop
