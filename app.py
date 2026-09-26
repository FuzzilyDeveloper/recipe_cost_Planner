from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Crumb & Co. | Recipe Costing",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
PRICE_FILE = ROOT / "data" / "ingredient_prices.csv"
SAMPLE_RECIPES: dict[str, dict[str, Any]] = {
    "Brown butter cookies": {
        "emoji": "🍪",
        "category": "COOKIE JAR",
        "yield": 24,
        "margin": 68,
        "ingredients": [
            {"name": "All-purpose flour", "quantity": 360.0},
            {"name": "Unsalted butter", "quantity": 225.0},
            {"name": "Brown sugar", "quantity": 220.0},
            {"name": "Chocolate chips", "quantity": 180.0},
            {"name": "Eggs", "quantity": 2.0},
            {"name": "Vanilla extract", "quantity": 5.0},
        ],
    },
    "Lemon loaf cake": {
        "emoji": "🍋",
        "category": "CAKE CASE",
        "yield": 10,
        "margin": 65,
        "ingredients": [
            {"name": "All-purpose flour", "quantity": 280.0},
            {"name": "Unsalted butter", "quantity": 170.0},
            {"name": "Caster sugar", "quantity": 210.0},
            {"name": "Eggs", "quantity": 3.0},
            {"name": "Whole milk", "quantity": 100.0},
            {"name": "Lemons", "quantity": 2.0},
        ],
    },
    "Cinnamon morning buns": {
        "emoji": "🥐",
        "category": "MORNING BAKE",
        "yield": 12,
        "margin": 70,
        "ingredients": [
            {"name": "Bread flour", "quantity": 500.0},
            {"name": "Unsalted butter", "quantity": 180.0},
            {"name": "Whole milk", "quantity": 220.0},
            {"name": "Brown sugar", "quantity": 140.0},
            {"name": "Eggs", "quantity": 2.0},
            {"name": "Ground cinnamon", "quantity": 12.0},
            {"name": "Instant yeast", "quantity": 7.0},
        ],
    },
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap');
    :root { --ink:#27332b; --muted:#727b70; --berry:#b5425c; --leaf:#557b59; --butter:#f2c14e; --paper:#faf8f1; }
    html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
    .stApp { background:var(--paper); color:var(--ink); background-image:radial-gradient(#d7d4c7 0.55px, transparent 0.55px); background-size:16px 16px; }
    [data-testid="stHeader"] { background:rgba(250,248,241,.88); }
    [data-testid="stSidebar"] { background:#f1eee3; border-right:1px solid #e5e0d2; }
    [data-testid="stSidebar"] > div:first-child { padding-top:1.4rem; }
    .brand { display:flex; align-items:center; gap:12px; padding:3px 0 20px; border-bottom:1px solid #ded9c9; margin-bottom:22px; }
    .brand-mark { width:44px; height:44px; border-radius:14px; display:grid; place-items:center; background:#f3cb66; font-size:24px; box-shadow:0 4px 0 #dfb34c; }
    .brand-name { color:var(--ink); font-family:'Fraunces',serif; font-size:20px; font-weight:700; line-height:1.1; }
    .brand-sub { color:var(--muted); font-size:10px; letter-spacing:1.45px; margin-top:4px; }
    .sidebar-note { border-radius:13px; background:#fffdf6; padding:13px 14px; margin:15px 0 5px; border:1px solid #e7e1d3; color:var(--muted); font-size:12px; line-height:1.55; }
    .topline { color:var(--leaf); font-size:11px; font-weight:700; letter-spacing:1.7px; margin:4px 0 6px; }
    .page-title { font-family:'Fraunces',serif; font-size:38px; font-weight:600; letter-spacing:0; line-height:1.12; color:var(--ink); margin:0; }
    .page-sub { color:var(--muted); font-size:14px; margin:8px 0 22px; }
    .recipe-banner { background:#e8efe1; border:1px solid #dce6d5; border-radius:18px; padding:17px 20px; display:flex; align-items:center; gap:14px; margin:0 0 18px; }
    .recipe-emoji { width:50px; height:50px; display:grid; place-items:center; border-radius:15px; background:#fffdf6; font-size:27px; }
    .recipe-name { font-family:'Fraunces',serif; font-size:24px; color:var(--ink); line-height:1.1; }
    .recipe-kicker { font-size:10px; color:var(--leaf); font-weight:700; letter-spacing:1.6px; margin-bottom:5px; }
    .recipe-caption { font-size:12px; color:var(--muted); margin-top:4px; }
    .section-heading { font-family:'Fraunces',serif; font-size:21px; color:var(--ink); margin:0 0 3px; }
    .section-caption { color:var(--muted); font-size:12px; margin:0 0 13px; }
    .metric-card { background:#fffdf7; border:1px solid #e9e3d6; border-radius:14px; padding:14px 16px; min-height:105px; }
    .metric-label { color:var(--muted); text-transform:uppercase; letter-spacing:1.1px; font-size:10px; font-weight:700; }
    .metric-value { color:var(--ink); font-family:'Fraunces',serif; font-size:27px; line-height:1.2; margin-top:7px; }
    .metric-foot { color:var(--muted); font-size:11px; margin-top:3px; }
    .price-highlight { background:#557b59; border-color:#557b59; }
    .price-highlight .metric-label, .price-highlight .metric-foot { color:#e0ebdc; }
    .price-highlight .metric-value { color:white; }
    div[data-testid="stDataEditor"] { border:1px solid #e9e3d6; border-radius:13px; overflow:hidden; background:#fffdf7; }
    div.stButton > button { border-radius:10px; font-weight:600; border-color:#d9d3c5; }
    div.stButton > button[kind="primary"] { background:#b5425c; border-color:#b5425c; color:white; }
    div.stButton > button[kind="primary"]:hover { background:#96354b; border-color:#96354b; }
    div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input { border-radius:9px; }
    .tip { background:#fff1d3; border:1px solid #f1dfb6; border-radius:12px; padding:12px 14px; color:#625338; font-size:12px; line-height:1.5; }
    .price-row { padding:9px 0; border-bottom:1px solid #eee9df; font-size:13px; }
    .price-row:last-child { border-bottom:0; }
    .pill { display:inline-block; border-radius:20px; padding:4px 9px; background:#f7e5e8; color:#9b3c51; font-size:10px; font-weight:700; letter-spacing:.7px; }
    .footer { text-align:center; color:#969486; font-size:10px; padding:28px 0 8px; }
    @keyframes arrive { from { opacity:0; transform:translateY(7px); } to { opacity:1; transform:translateY(0); } }
    .block-container { animation:arrive .4s ease-out both; padding-top:2rem; padding-bottom:2rem; max-width:1440px; }
    @media(max-width:700px) { .page-title{font-size:31px}.recipe-name{font-size:20px}.metric-value{font-size:23px} }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_price_book() -> pd.DataFrame:
    if PRICE_FILE.exists():
        return pd.read_csv(PRICE_FILE)
    return pd.DataFrame(
        [
            ["All-purpose flour", "g", 0.0015, "Pantry"],
            ["Bread flour", "g", 0.0018, "Pantry"],
            ["Unsalted butter", "g", 0.0092, "Dairy"],
            ["Caster sugar", "g", 0.0024, "Pantry"],
            ["Brown sugar", "g", 0.0031, "Pantry"],
            ["Chocolate chips", "g", 0.0105, "Treats"],
            ["Eggs", "each", 0.34, "Dairy"],
            ["Vanilla extract", "ml", 0.045, "Pantry"],
            ["Whole milk", "ml", 0.0018, "Dairy"],
            ["Lemons", "each", 0.48, "Produce"],
            ["Ground cinnamon", "g", 0.012, "Pantry"],
            ["Instant yeast", "g", 0.018, "Pantry"],
        ],
        columns=["ingredient", "unit", "price", "category"],
    )


def money(amount: float) -> str:
    return f"${amount:,.2f}"


def initialize_state() -> None:
    if "recipes" not in st.session_state:
        st.session_state.recipes = {
            name: {**recipe, "ingredients": [dict(row) for row in recipe["ingredients"]]}
            for name, recipe in SAMPLE_RECIPES.items()
        }
    if "active_recipe" not in st.session_state:
        st.session_state.active_recipe = next(iter(SAMPLE_RECIPES))
    if "ingredient_counter" not in st.session_state:
        st.session_state.ingredient_counter = 0
    if "editing_prices" not in st.session_state:
        st.session_state.editing_prices = False


initialize_state()
price_book = read_price_book()
price_lookup = price_book.set_index("ingredient").to_dict("index")
recipe_names = list(st.session_state.recipes)

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">🥐</div><div><div class="brand-name">Crumb & Co.</div><div class="brand-sub">BAKERY WORKSHOP</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("**YOUR RECIPE BOOK**")
    selected = st.selectbox(
        "Choose a recipe",
        recipe_names,
        index=recipe_names.index(st.session_state.active_recipe),
        key="active_recipe_selector",
        label_visibility="collapsed",
    )
    if selected != st.session_state.active_recipe:
        st.session_state.active_recipe = selected
        st.rerun()

    if st.button("＋  Start a new recipe", use_container_width=True):
        st.session_state.show_new_recipe = True
    st.markdown(
        '<div class="sidebar-note"><b>Little bakery, clear numbers.</b><br>Price each batch, spot your biggest costs and set a shelf price that pays you back.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▦  Ingredient price book", use_container_width=True):
        st.session_state.editing_prices = not st.session_state.editing_prices

if st.session_state.get("show_new_recipe"):
    with st.sidebar.form("new_recipe_form"):
        new_recipe_name = st.text_input("Recipe name", placeholder="e.g. Raspberry scones")
        submitted = st.form_submit_button("Create recipe", type="primary", use_container_width=True)
        if submitted and new_recipe_name.strip():
            new_recipe_name = new_recipe_name.strip()
            if new_recipe_name in st.session_state.recipes:
                st.warning("That recipe name is already in your book.")
            else:
                st.session_state.recipes[new_recipe_name] = {
                    "emoji": "🧁",
                    "category": "NEW RECIPE",
                    "yield": 12,
                    "margin": 68,
                    "ingredients": [],
                }
                st.session_state.active_recipe = new_recipe_name
                st.session_state.active_recipe_selector = new_recipe_name
                st.session_state.show_new_recipe = False
                st.rerun()

active_name = st.session_state.active_recipe
recipe = st.session_state.recipes[active_name]
st.markdown('<div class="topline">YOUR LITTLE BAKERY, BIG PICTURE</div>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Recipe costing</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Know what each bake costs. Price it with confidence.</p>', unsafe_allow_html=True)
st.markdown(
    f'<div class="recipe-banner"><div class="recipe-emoji">{recipe["emoji"]}</div><div><div class="recipe-kicker">{recipe["category"]}</div><div class="recipe-name">{active_name}</div><div class="recipe-caption">A good bake starts with a recipe. A good business knows its numbers.</div></div></div>',
    unsafe_allow_html=True,
)

settings_col1, settings_col2, settings_col3 = st.columns([1, 1, 2])
with settings_col1:
    recipe["yield"] = st.number_input(
        "Pieces per batch", min_value=1, max_value=10000, value=int(recipe["yield"]), step=1
    )
with settings_col2:
    recipe["margin"] = st.number_input(
        "Target gross margin (%)", min_value=0, max_value=95, value=int(recipe["margin"]), step=1
    )
with settings_col3:
    st.markdown(
        '<div class="tip" style="margin-top:27px"><b>Quick tip</b> · Gross margin is the share of your selling price left after ingredients. Labour and packaging are not included in this demo.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-heading">What goes into the batch?</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Change quantities or ingredients below. Costs update as you work.</div>', unsafe_allow_html=True)

if not recipe["ingredients"]:
    recipe["ingredients"].append({"name": price_book.iloc[0]["ingredient"], "quantity": 100.0})

editor_rows = []
for row in recipe["ingredients"]:
    editor_rows.append(
        {
            "Ingredient": row["name"],
            "Amount": float(row["quantity"]),
        }
    )
editor_frame = pd.DataFrame(editor_rows)
edited_frame = st.data_editor(
    editor_frame,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    key=f"ingredient_editor_{active_name}_{len(recipe['ingredients'])}",
    column_config={
        "Ingredient": st.column_config.SelectboxColumn(
            "Ingredient", options=price_book["ingredient"].tolist(), required=True, width="large"
        ),
        "Amount": st.column_config.NumberColumn("Quantity", min_value=0.0, step=10.0, format="%.1f"),
    },
)
recipe["ingredients"] = [
    {"name": row["Ingredient"], "quantity": float(row["Amount"])}
    for _, row in edited_frame.iterrows()
]
live_cost_rows = []
for row in recipe["ingredients"]:
    price_info = price_lookup.get(row["name"], {"unit": "g", "price": 0.0})
    live_cost_rows.append(
        {
            "Ingredient": row["name"],
            "Quantity": f"{row['quantity']:g} {price_info['unit']}",
            "Price / unit": money(float(price_info["price"])),
            "Line cost": money(float(row["quantity"]) * float(price_info["price"])),
        }
    )
st.dataframe(pd.DataFrame(live_cost_rows), use_container_width=True, hide_index=True)

add_col, remove_col, download_col = st.columns([1, 1, 3])
with add_col:
    if st.button("＋  Add ingredient", type="primary"):
        recipe["ingredients"].append(
            {"name": price_book.iloc[0]["ingredient"], "quantity": 100.0}
        )
        st.rerun()
with remove_col:
    if st.button("−  Remove last") and len(recipe["ingredients"]) > 1:
        recipe["ingredients"].pop()
        st.rerun()

ingredient_cost = sum(
    float(row["quantity"]) * float(price_lookup.get(row["name"], {}).get("price", 0.0))
    for row in recipe["ingredients"]
)
packaging_cost = 0.18 * int(recipe["yield"])
full_batch_cost = ingredient_cost + packaging_cost
unit_cost = full_batch_cost / int(recipe["yield"])
margin = int(recipe["margin"]) / 100
suggested_price = unit_cost / (1 - margin) if margin < 1 else 0.0
profit_per_piece = suggested_price - unit_cost

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-heading">The numbers at a glance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">A quick read on this batch, from mixing bowl to display case.</div>', unsafe_allow_html=True)
metric_data = [
    ("INGREDIENTS / BATCH", money(ingredient_cost), "Your recipe, priced by weight"),
    ("FULL BATCH COST", money(full_batch_cost), f"Includes {money(packaging_cost)} packaging estimate"),
    ("COST PER PIECE", money(unit_cost), f"Based on {int(recipe['yield'])} pieces"),
    ("SUGGESTED SHELF PRICE", money(suggested_price), f"{money(profit_per_piece)} gross profit / piece"),
]
metric_cols = st.columns(4)
for index, (label, value, footnote) in enumerate(metric_data):
    card_class = "metric-card price-highlight" if index == 3 else "metric-card"
    metric_cols[index].markdown(
        f'<div class="{card_class}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{footnote}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1.15, 0.85], gap="large")
with left:
    st.markdown('<div class="section-heading">Where the money goes</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Your biggest ingredient costs, in order.</div>', unsafe_allow_html=True)
    breakdown = pd.DataFrame(
        [
            {"Ingredient": row["name"], "Cost": row["quantity"] * price_lookup.get(row["name"], {}).get("price", 0.0)}
            for row in recipe["ingredients"]
        ]
    )
    if not breakdown.empty:
        breakdown = breakdown.groupby("Ingredient", as_index=False)["Cost"].sum().sort_values("Cost", ascending=True)
        st.bar_chart(breakdown, x="Ingredient", y="Cost", color="#b5425c", horizontal=True)
with right:
    st.markdown('<div class="section-heading">Price book</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Your sample ingredient costs. Edit the CSV to make them yours.</div>', unsafe_allow_html=True)
    if st.session_state.editing_prices:
        editable_prices = st.data_editor(
            price_book,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="price_book_editor",
            column_config={"price": st.column_config.NumberColumn("Price / unit ($)", min_value=0.0, format="$%.4f")},
        )
        if st.button("Save price book", type="primary"):
            PRICE_FILE.parent.mkdir(parents=True, exist_ok=True)
            editable_prices.to_csv(PRICE_FILE, index=False)
            st.session_state.editing_prices = False
            st.rerun()
    else:
        for _, ingredient in price_book.sort_values("category").iterrows():
            st.markdown(
                f'<div class="price-row"><b>{ingredient["ingredient"]}</b><span style="float:right;color:#727b70">{money(float(ingredient["price"]))} / {ingredient["unit"]}</span></div>',
                unsafe_allow_html=True,
            )

csv_buffer = io.StringIO()
csv_writer = csv.writer(csv_buffer)
csv_writer.writerow(["Ingredient", "Quantity", "Unit", "Price per unit", "Line cost"])
for row in recipe["ingredients"]:
    info = price_lookup.get(row["name"], {"unit": "g", "price": 0.0})
    csv_writer.writerow([row["name"], row["quantity"], info["unit"], info["price"], row["quantity"] * info["price"]])
csv_writer.writerow([])
csv_writer.writerow(["Yield", int(recipe["yield"])])
csv_writer.writerow(["Ingredient cost / batch", round(ingredient_cost, 2)])
csv_writer.writerow(["Packaging estimate / batch", round(packaging_cost, 2)])
csv_writer.writerow(["Full batch cost", round(full_batch_cost, 2)])
csv_writer.writerow(["Cost per piece", round(unit_cost, 2)])
csv_writer.writerow(["Suggested shelf price", round(suggested_price, 2)])
with download_col:
    st.download_button(
        "↓  Export recipe costing CSV",
        data=csv_buffer.getvalue(),
        file_name=f"{active_name.lower().replace(' ', '-')}-costing.csv",
        mime="text/csv",
    )

st.markdown('<div class="footer">MADE WITH A LITTLE FLOUR, A LITTLE CARE & A LOT OF GOOD MATH</div>', unsafe_allow_html=True)
