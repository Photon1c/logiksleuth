import matplotlib.pyplot as plt

def yearly_gap_chart(yearly_df, title: str):
    fig = plt.figure(figsize=(9,5))
    plt.plot(yearly_df["Year"], yearly_df["total"], label="Total")
    plt.plot(yearly_df["Year"], yearly_df["solved"], label="Solved")
    plt.fill_between(yearly_df["Year"], yearly_df["solved"], yearly_df["total"], alpha=0.3)
    plt.title(title)
    plt.xlabel("Year"); plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    return fig

def unsolved_share_bar(yearly_df, title: str):
    share = (yearly_df["total"] - yearly_df["solved"]) / yearly_df["total"]
    fig = plt.figure(figsize=(9,3))
    plt.bar(yearly_df["Year"], share)
    plt.title(title)
    plt.xlabel("Year"); plt.ylabel("Unsolved share")
    plt.tight_layout()
    return fig
