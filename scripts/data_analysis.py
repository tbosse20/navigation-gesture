import pandas as pd

def plot_distribution(data, title="Data Distribution", xlabel="Value", ylabel="Frequency"):
    """
    Plot the distribution of a dataset using a histogram.

    Args:
        data (list or np.ndarray): The data to plot.
        title (str): The title of the plot.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30, alpha=0.7, color='blue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y', alpha=0.75)
    plt.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot data distribution.")
    # Folder 
    parser.add_argument(
        "data_folder",
        type=str,
        help="Path to the folder containing data files.",
    )
    args = parser.parse_args()
    
    