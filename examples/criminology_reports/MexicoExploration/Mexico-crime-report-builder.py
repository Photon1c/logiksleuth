import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns



import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Save all plots to a single PDF
with PdfPages('Criminology_Report.pdf') as pdf:
    figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        pdf.savefig(fig, bbox_inches='tight')

# Optionally, convert PDF to HTML if required using external tools (e.g., pandoc)



# Load your CSV dataset
df = pd.read_csv(r"F:\SquirrelPI\mexdata\mexico_crime.csv")

# Load your shapefile
states_map = gpd.read_file(r"F:\SquirrelPI\mexican-states.shp")

# Merge function to create geographical data
def merge_data(df, states_map):
    agg_df = df.groupby('entity', as_index=False)['count'].sum()
    merged = states_map.merge(agg_df, left_on='name', right_on='entity', how='left').fillna(0)
    return merged

# Function to plot heatmap by region
def plot_crime_heatmap(merged, title, cmap='Reds'):
    fig, ax = plt.subplots(figsize=(12, 8))
    merged.plot(column='count', cmap=cmap, linewidth=0.5, edgecolor='k', legend=True, ax=ax)
    plt.title(title, fontsize=15)
    plt.axis('off')
    plt.show()

# Function to plot yearly crime trends
def plot_yearly_trends(df):
    plt.figure(figsize=(10,5))
    yearly = df.groupby('year')['count'].sum()
    yearly.plot(kind='bar')
    plt.title("Yearly Crime Trends")
    plt.xlabel("Year")
    plt.ylabel("Total Crime Count")
    plt.show()

# Function to visualize type/subtype of crime
def plot_crime_types(df):
    crime_type = df.groupby('type_of_crime')['count'].sum().sort_values()
    crime_type.plot(kind='barh', figsize=(8,6))
    plt.title("Crime Counts by Type")
    plt.xlabel("Total Counts")
    plt.ylabel("Crime Type")
    plt.show()

# Function to visualize monthly patterns
def plot_monthly_patterns(df):
    months_order = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
    monthly = df.groupby('month')['count'].sum().reindex(months_order)
    monthly.plot(kind='line', marker='o', figsize=(10,6))
    plt.title("Monthly Crime Patterns")
    plt.xlabel("Month")
    plt.ylabel("Crime Counts")
    plt.xticks(rotation=45)
    plt.show()

# Additional informative charts:
# Modality breakdown
def plot_crime_modalities(df):
    modality = df.groupby('modality')['count'].sum().sort_values(ascending=False).head(10)
    modality.plot(kind='bar', figsize=(10,6))
    plt.title("Top 10 Crime Modalities")
    plt.xlabel("Modality")
    plt.ylabel("Total Counts")
    plt.xticks(rotation=45)
    plt.show()

# Subtype breakdown
def plot_subtype_breakdown(df):
    subtype = df.groupby('subtype_of_crime')['count'].sum().sort_values(ascending=False).head(10)
    subtype.plot(kind='bar', figsize=(10,6))
    plt.title("Top 10 Subtypes of Crime")
    plt.xlabel("Subtype of Crime")
    plt.ylabel("Total Counts")
    plt.xticks(rotation=45)
    plt.show()

# Detailed breakdown by type, subtype, modality
def plot_detailed_breakdown(df):
    detailed = df.groupby(['type_of_crime', 'subtype_of_crime', 'modality'])['count'] \
                 .sum().sort_values(ascending=False).head(10)
    detailed.plot(kind='barh', figsize=(12,8))
    plt.title("Top 10 Detailed Crime Combinations")
    plt.xlabel("Total Counts")
    plt.ylabel("Crime Combination")
    plt.show()

# Generate all plots
merged_data = merge_data(df, states_map)
plot_crime_heatmap(merged_data, "Crime Heatmap by Region")
plot_yearly_trends(df)
plot_crime_types(df)
plot_monthly_patterns(df)
plot_crime_modalities(df)
plot_subtype_breakdown(df)
plot_detailed_breakdown(df)
