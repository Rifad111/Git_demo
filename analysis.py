"""
COVID-19 Global Data Analysis
------------------------------
Analyzes COVID-19 case, death, and vaccination trends using the
Our World in Data dataset, with a focus on Bangladesh compared to
other major countries.

Author: Mahmudul
Data source: https://github.com/owid/covid-19-data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# 1. CONFIG
# ---------------------------------------------------------
DATA_PATH = "data/covid_19.csv"
OUTPUT_DIR = "visuals"

COUNTRIES_TO_COMPARE = [
    "Bangladesh", "India", "United States", "United Kingdom", "Brazil"
]

sns.set_theme(style="darkgrid")
plt.rcParams["figure.dpi"] = 120


# ---------------------------------------------------------
# 2. LOAD & CLEAN DATA
# ---------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    """Load the raw CSV and apply basic cleaning."""
    df = pd.read_csv(path, parse_dates=["date"])

    # Keep only real countries — OWID also includes aggregate rows
    # like "World", "Asia", "High-income countries" etc. which have
    # no value in the 'continent' column.
    df = df[df["continent"].notna()].copy()

    # Keep only the columns we actually need for this analysis
    columns_needed = [
        "location", "date", "total_cases", "new_cases",
        "total_deaths", "new_deaths", "people_fully_vaccinated",
        "population"
    ]
    df = df[columns_needed]

    # Fill missing daily counts with 0 (no report that day != unknown)
    df[["new_cases", "new_deaths"]] = df[["new_cases", "new_deaths"]].fillna(0)

    return df


def get_latest_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Return the most recent row available for every country."""
    return df.sort_values("date").groupby("location").tail(1)


# ---------------------------------------------------------
# 3. VISUALIZATIONS
# ---------------------------------------------------------
def plot_case_trend(df: pd.DataFrame, countries: list, out_path: str):
    """Line chart: total confirmed cases over time for selected countries."""
    subset = df[df["location"].isin(countries)]

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=subset, x="date", y="total_cases", hue="location", linewidth=2)
    plt.title("Total Confirmed COVID-19 Cases Over Time", fontsize=14, weight="bold")
    plt.xlabel("Date")
    plt.ylabel("Total Cases")
    plt.legend(title="Country")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_top_countries(latest: pd.DataFrame, out_path: str, top_n: int = 10):
    """Bar chart: countries with the highest total case counts."""
    top = latest.nlargest(top_n, "total_cases").sort_values("total_cases")

    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x="total_cases", y="location", hue="location",
                palette="viridis", legend=False)
    plt.title(f"Top {top_n} Countries by Total COVID-19 Cases", fontsize=14, weight="bold")
    plt.xlabel("Total Cases")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_death_rate(latest: pd.DataFrame, countries: list, out_path: str):
    """Bar chart: case fatality rate (%) for selected countries."""
    subset = latest[latest["location"].isin(countries)].copy()
    subset["fatality_rate"] = (subset["total_deaths"] / subset["total_cases"]) * 100
    subset = subset.sort_values("fatality_rate")

    plt.figure(figsize=(9, 5))
    sns.barplot(data=subset, x="fatality_rate", y="location", hue="location",
                palette="rocket", legend=False)
    plt.title("Case Fatality Rate by Country (%)", fontsize=14, weight="bold")
    plt.xlabel("Deaths per 100 Confirmed Cases")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_bangladesh_vaccination(df: pd.DataFrame, out_path: str):
    """Area chart: Bangladesh's fully-vaccinated population over time."""
    bd = df[df["location"] == "Bangladesh"].dropna(subset=["people_fully_vaccinated"])

    plt.figure(figsize=(10, 6))
    plt.fill_between(bd["date"], bd["people_fully_vaccinated"], color="#2a9d8f", alpha=0.6)
    plt.plot(bd["date"], bd["people_fully_vaccinated"], color="#264653", linewidth=2)
    plt.title("Bangladesh: Fully Vaccinated Population Over Time", fontsize=14, weight="bold")
    plt.xlabel("Date")
    plt.ylabel("People Fully Vaccinated")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


# ---------------------------------------------------------
# 4. MAIN
# ---------------------------------------------------------
def main():
    df = load_data(DATA_PATH)
    latest = get_latest_snapshot(df)

    print("Dataset loaded:", df.shape[0], "rows,", df["location"].nunique(), "countries")

    plot_case_trend(df, COUNTRIES_TO_COMPARE, f"{OUTPUT_DIR}/case_trend.png")
    plot_top_countries(latest, f"{OUTPUT_DIR}/top_countries.png")
    plot_death_rate(latest, COUNTRIES_TO_COMPARE, f"{OUTPUT_DIR}/fatality_rate.png")
    plot_bangladesh_vaccination(df, f"{OUTPUT_DIR}/bangladesh_vaccination.png")

    print("All charts saved to the 'visuals/' folder.")


if __name__ == "__main__":
    main()
