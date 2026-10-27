
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display, clear_output

# 1. Load dataset
df = px.data.gapminder()

# 2. Create dropdown
dropdown = widgets.Dropdown(
    options={
        "Population": "pop",
        "Life Expectancy": "lifeExp",
        "GDP per Capita": "gdpPercap"
    },
    value="pop",
    description="Variable:"
)

# 3. Create year slider
year_slider = widgets.IntSlider(
    value=2007,
    min=1952,
    max=2007,
    step=5,
    description="Year:",
    continuous_update=False
)

# 4. Function to draw the map
def draw_map(variable, year):

    # Filter data by selected year
    data = df[df["year"] == year]

    # Plot interactive map
    fig = px.choropleth(
        data,
        locations="iso_alpha",
        color=variable,
        hover_name="country",
        hover_data=["continent", "pop", "lifeExp", "gdpPercap"],
        color_continuous_scale="Viridis",
        projection="natural earth",
        title=f"World Map - {variable} ({year})"
    )

    fig.show()

# 5. Connect widgets to function
output = widgets.interactive_output(
    draw_map,
    {
        "variable": dropdown,
        "year": year_slider
    }
)

# 6. Display dropdown, slider and map
display(widgets.VBox([
    dropdown,
    year_slider,
    output
]))
