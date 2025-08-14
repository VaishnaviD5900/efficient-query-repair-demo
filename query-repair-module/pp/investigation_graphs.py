import pandas as pd
import numpy as np
from numpy import arange,power
import matplotlib
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import os
import matplotlib.ticker as ticker
matplotlib.use('PDF')
matplotlib.use('TkAgg') 
import re

class investigation_graphs:

    def plot_time_by_constraint_Distance(self, measure, dataSize):
        directory_path = '/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/Distance_A'
        file_path = f'Run_info_{dataSize}_size50000_H'

        # Drop duplicate constraints to ensure each appears only once
        file_path_csv = os.path.join(directory_path, f'{file_path}.csv')

        # Read the CSV file
        df = pd.read_csv(file_path_csv, sep=",")

        # Clean and filter necessary columns
        df = df[['Data Name', 'Type', 'Query Num', 'Distance', measure]].dropna()

        # Sort the DataFrame by Distance
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')
        df = df.sort_values(by='Distance')

        # Determine global x-axis range
        global_min = df['Distance'].min()
        global_max = df['Distance'].max()

        # Define a color scheme for measures
        color_pairs = {
            "Time": ['blue', 'red'],
            "Checked Num": ['blue', 'red'],
            "Access Num": ['blue', 'red']
        }
        colors = color_pairs.get(measure, ['gray', 'black'])

        # Create a unique figure with 3 subplots (1 row, 3 columns)
        unique_queries = sorted(df['Query Num'].unique())
        fig, axes = plt.subplots(1, len(unique_queries), figsize=(15, 5), sharey=True)

        if len(unique_queries) == 1:  # Ensure axes are iterable for a single query
            axes = [axes]

        for i, query_num in enumerate(unique_queries):
            ax = axes[i]

            # Filter data for the current Query Num
            query_df = df[df['Query Num'] == query_num]

            # Group by Type and aggregate
            for j, (type_name, group) in enumerate(query_df.groupby('Type')):
                aggregated = group.groupby('Distance', as_index=False)[measure].mean()
                ax.plot(
                    aggregated['Distance'],
                    aggregated[measure],
                    marker='o',
                    linestyle='-',
                    color=colors[j % len(colors)],  # Alternate between the two colors
                    label=type_name
                )
                
            # Customize each subplot
            ax.set_title(f'Query {query_num}', fontsize=30)
            ax.set_xlabel('Exploration Distance', fontsize=27)
            if i == 0:
                if measure == 'Time':
                    ax.set_ylabel('Runtime (sec)', fontsize=30)
                if measure == 'Checked Num':
                    ax.set_ylabel('NCE', fontsize=30)
                if measure == 'Access Num':
                    ax.set_ylabel('NCA', fontsize=30)

            ax.grid(True)
            ax.tick_params(axis='y', labelsize=27)  # Change the size of y-axis tick labels
            ax.tick_params(axis='x', labelsize=25)
            ax.legend(fontsize=25)

            # Ensure consistent x-axis scaling
            ax.set_xlim(global_min, global_max)

        # Add a global title and adjust layout
        #fig.suptitle(f'{measure} vs Distance for Different Queries', fontsize=18)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Save the figure as a PDF in the specified directory
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)  # Create the directory if it doesn't exist
        output_file = os.path.join(directory_path, f'{measure}_vs_constraint_distance_combined_{dataSize}.pdf')
        plt.savefig(output_file)
        plt.show()

        print(f"Graph saved to: {output_file}")

    def natural_sort_key(self, text):
        """Splits text into numeric and non-numeric parts for correct sorting."""
        return [int(num) if num.isdigit() else num for num in re.split(r'(\d+)', text)]

    def Generate_Time_vs_Constraints(self, measure):

        # Load the CSV file into a DataFrame
        file_path = "/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/Time_vs_Constraints_A"  # Update this path
        file_path_csv = os.path.join(file_path, 'Run_info_Healthcare_size50000_H_brute.csv')
        # Read the CSV file
        df = pd.read_csv(file_path_csv, sep=",")

        # Filter and clean the necessary columns
        df = df[['Query Num', 'Con Name', 'Type', measure]].dropna()

        # Define color mapping for the measure
        color_mapping = {
            "Time": {"BF": "green", "FF": "blue", "RP": "red"},
            "Checked Num": {"BF": "green", "FF": "blue", "RP": "red"},
            "Access Num": {"BF": "green", "FF": "blue", "RP": "red"}
        }
        colors = color_mapping.get(measure, {"BF": "green", "FF": "blue", "RP": "red"})

        # Create a figure with 3 subplots for the 3 queries
        fig, axes = plt.subplots(1, 2, figsize=(18, 5), sharey=True)  # Share y-axis for consistent comparison

        # Iterate through each query
        for i, query_num in enumerate([1, 2]):
            ax = axes[i]

            # Filter the DataFrame for the specified Query Num
            query_df = df[df['Query Num'] == query_num]


            # Pivot the data to prepare for plotting
            pivot_df = query_df.pivot_table(index=['Con Name'], columns='Type', values=measure, aggfunc='mean').reset_index()
            pivot_df = pivot_df.sort_values(by=["Con Name"], key=lambda x: x.map(self.natural_sort_key))

            # Bar positions and labels
            x = range(len(pivot_df))
            labels = pivot_df['Con Name']

            # Plot bars for each type with assigned colors
            if 'BF' in pivot_df:
                ax.bar(x, pivot_df['BF'], width=0.3, label='BF', align='center', color=colors["BF"])
            if 'FF' in pivot_df:
                ax.bar([pos + 0.3 for pos in x], pivot_df['FF'], width=0.3, label='FF', align='center', color=colors["FF"])
            if 'RP' in pivot_df:
                ax.bar([pos + 0.6 for pos in x], pivot_df['RP'], width=0.3, label='RP', align='center', color=colors["RP"])

            ax.set_yscale('log')

            # Ensure all values are ≥ 1 for log scale
            ax.set_ylim(bottom=max(1, df[measure].min() * 1.0), top=df[measure].max() * 2.0)

            # Customize each subplot
            ax.set_title(f'Query: {query_num}', fontsize=40)
            ax.set_xlabel('Constraint', fontsize=40)
            ax.set_xticks([pos + 0.3 for pos in x])
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=40)
            if i == 0:  # Add y-axis label to the first subplot
                if measure == "Time":
                    ax.set_ylabel('Runtime (sec)', fontsize=40)
                elif measure == "Checked Num":
                    ax.set_ylabel('NCE', fontsize=40)
                elif measure == "Access Num":
                    ax.set_ylabel('NCA', fontsize=40)
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
            ax.tick_params(axis='y', labelsize=40)  # Change the size of y-axis tick labels
        # Add legend to the last subplot
        axes[-1].legend(fontsize=18)

        # Adjust layout for better readability
        plt.tight_layout()

        # Save the figure as a PDF
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        output_file = os.path.join(file_path, f'comparison_fully_vs_ranges_bruteforce_{measure}.pdf')
        plt.savefig(output_file)
        plt.show()

        print(f"Graph saved to: {output_file}")

    def Generate_Time_vs_Constraints_Erica(self, measure1, measure2):
        # Load the CSV file into a DataFrame
        file_path = "/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/Erica"  # Update this path
        file_path_csv = os.path.join(file_path, 'Erica.csv')
        df = pd.read_csv(file_path_csv, sep=",")

        # Filter and clean the necessary columns
        df = df[['Constraint', 'Type', measure1, measure2]].dropna()

        # Define color mapping
        color_mapping = {
            "FF": "blue",
            "RP": "red",
            "Erica": "purple"
        }

        # Create separate figures for Prov Time and Search Time
        fig1, ax1 = plt.subplots(figsize=(12, 6))  # Prov Time plot
        fig2, ax2 = plt.subplots(figsize=(12, 7.7))  # Search Time plot

        # Pivot data to prepare for plotting
        pivot_df = df.pivot_table(index=['Constraint'], columns='Type', values=[measure1, measure2], aggfunc='mean').reset_index()

        # Bar positions and labels
        x = range(len(pivot_df))
        labels = pivot_df['Constraint']
        bar_width = 0.3  # Space bars apart

        # Plot for Prov Time
        for i, type_name in enumerate(color_mapping.keys()):
            if (measure1, type_name) in pivot_df:
                prov_times = pivot_df[(measure1, type_name)].fillna(0)
                positions = [pos + i * bar_width for pos in x]  # Adjust x positions
                ax1.bar(positions, prov_times, width=bar_width, label=type_name, color=color_mapping[type_name])

        #ax1.set_title('Provenance Time', fontsize=18)
        ax1.set_xlabel('Constraint', fontsize=50)
        ax1.set_ylabel('Search Time (sec)', fontsize=45)
        ax1.set_xticks([pos + bar_width for pos in x])  # Center x-ticks
        ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=45)
        ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax1.legend(fontsize=30)
        ax1.tick_params(axis='y', labelsize=41)  # Change the size of y-axis tick labels
        # Plot for Search Time
        for i, type_name in enumerate(color_mapping.keys()):
            if (measure2, type_name) in pivot_df:
                search_times = pivot_df[(measure2, type_name)].fillna(0)
                positions = [pos + i * bar_width for pos in x]  # Adjust x positions
                ax2.bar(positions, search_times, width=bar_width, label=type_name, color=color_mapping[type_name])

        #ax2.set_title('Search Time', fontsize=30)
        ax2.set_xlabel('Constraint', fontsize=50)
        ax2.set_ylabel('Pre-processing \nTime (sec)', fontsize=45)
        ax2.set_xticks([pos + bar_width for pos in x])  # Center x-ticks
        ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=45)
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax2.legend(fontsize=30)
        ax2.tick_params(axis='y', labelsize=45)  # Change the size of y-axis tick labels
        # Adjust layout and save figures
        plt.tight_layout()

        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        search_output = os.path.join(file_path, 'search_time_comparison.pdf')
        prov_output = os.path.join(file_path, 'prov_time_comparison.pdf')

        fig1.savefig(prov_output, bbox_inches="tight")
        fig2.savefig(search_output, bbox_inches="tight")

        plt.show()

        print(f"Prov Time graph saved to: {prov_output}")
        print(f"Search Time graph saved to: {search_output}")