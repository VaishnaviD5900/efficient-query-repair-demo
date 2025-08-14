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

class genGraph:
    def __init__(self, directory_path):
        self.directory_path = directory_path

    def natural_sort_key(self, text):
        """Splits text into numeric and non-numeric parts for correct sorting."""
        return [int(num) if num.isdigit() else num for num in re.split(r'(\d+)', text)]

    def Generate_Time_vs_Constraints(self, measure, dataName):
        # Load the CSV file into a DataFrame
        file_path = "/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/Time_vs_Constraints_A"
        file_path_csv = os.path.join(file_path, f'Run_info_{dataName}_size50000_H.csv')
        df = pd.read_csv(file_path_csv, sep=",")

        # Filter and clean the necessary columns
        df = df[['Query Num', 'Con Name', 'Type', measure]].dropna()

        # Pivot the data to prepare for plotting
        pivot_df = df.pivot_table(index=['Query Num', 'Con Name'], columns='Type', values=measure, aggfunc='mean').reset_index()
        
        # Extract groups from Con Name (e.g., C1, C2)
        pivot_df['Group'] = pivot_df['Con Name'].str.extract('(C\\d+)')

        # Define color mapping for groups
        group_color_mapping = {
            "C3": {"FF": "blue", "RP": "red"},
            "C4": {"FF": "blue", "RP": "red"},
        }

        # Create a bar plot for each Query Num
        unique_queries = pivot_df['Query Num'].unique()
        pivot_df = pivot_df.sort_values(by=["Con Name"], key=lambda x: x.map(self.natural_sort_key))
        
        fig, axes = plt.subplots(1, len(unique_queries), figsize=(15, 5), sharey=True)

        for i, query_num in enumerate(unique_queries):
            ax = axes[i]
            query_data = pivot_df[pivot_df['Query Num'] == query_num]

            # Sort by group and Con Name
            #query_data = query_data.sort_values(by=['Group', 'Con Name'])

            # Bar positions and labels
            x = range(len(query_data))
            labels = query_data['Con Name']
            
            # Boolean flags to ensure each type (FF, RP) appears only once in the legend
            added_labels = {"FF": False, "RP": False}

            # Plot bars for each group with corresponding colors
            for group_name, group_data in query_data.groupby('Group'):
                bar_indices = [j for j, group in enumerate(query_data['Group']) if group == group_name]
                fully_color = group_color_mapping[group_name]["FF"]
                ranges_color = group_color_mapping[group_name]["RP"]

                # Plot FF bars
                if "FF" in group_data.columns:
                    label = "FF" if not added_labels["FF"] else None  # Add label only once
                    ax.bar([x[idx] for idx in bar_indices], group_data['FF'], width=0.4, label=label, color=fully_color)
                    added_labels["FF"] = True

                # Plot RP bars
                if "RP" in group_data.columns:
                    label = "RP" if not added_labels["RP"] else None  # Add label only once
                    ax.bar([x[idx] + 0.4 for idx in bar_indices], group_data['RP'], width=0.4, label=label, color=ranges_color)
                    added_labels["RP"] = True
            
                ax.set_yscale('log')

                # Ensure all values are ≥ 1 for log scale
                ax.set_ylim(bottom=max(1, df[measure].min() * 1.0), top=df[measure].max() * 2.0)


            # Customize the plot
            ax.set_title(f'Query: {query_num}', fontsize=30)
            ax.set_xlabel('Constraint', fontsize=30)
            ax.set_xticks([pos + 0.2 for pos in x])
            ax.set_xticklabels(labels, rotation=70, ha='right', fontsize=25)
            if i == 0:
                ax.set_ylabel('Runtime (sec)' if measure == "Time" else             
                'NCE' if measure == "Checked Num" else 
                'NCA' if measure == "Access Num" else 
                measure, 
                fontsize=30
            )

            ax.tick_params(axis='y', labelsize=30)
            ax.legend(fontsize=18)
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        output_file = os.path.join(file_path, f'comparison_fully_vs_ranges_{measure}_{dataName}.pdf')
        plt.savefig(output_file)
        plt.show()
        print(f"Graph saved to: {output_file}")

    def Generate_Time_vs_factors(self, measure, factor_type, dataName):
        # Load the CSV file into a DataFrame
        file_path = f"/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/{factor_type}"
        file_path_csv = os.path.join(file_path, f'Run_info_{dataName}_size50000_constraint3_{factor_type}.csv')
        #file_path_csv = os.path.join(file_path, f'Run_info_TPC-H.csv')
        df = pd.read_csv(file_path_csv, sep=",")
        dataName= df['Data Name'][0]

        # Filter and clean the necessary columns
        df = df[['Query Num', factor_type, 'Type', measure]].dropna()

        # Pivot the data to prepare for plotting
        pivot_df = df.pivot_table(index=['Query Num', factor_type], columns='Type', values=measure, aggfunc='mean').reset_index()

        # Extract groups from BranchNum
        pivot_df['Group'] = pivot_df[factor_type]

        # Create a bar plot for the single Query Num
        query_num = pivot_df['Query Num'].iloc[0]  # Get the single query number
        query_data = pivot_df[pivot_df['Query Num'] == query_num]

        # Sort by Group and BranchNum
        query_data = query_data.sort_values(by=['Group', factor_type])

        # Set up figure
        fig, ax = plt.subplots(figsize=(10, 6), sharey=True)

        # Bar positions and labels
        x = range(len(query_data))
        labels = query_data[factor_type].astype(int)


        # Define color scheme for each measure (each type gets a different shade)
        measure_colors = {
            "Time": {"FF": "blue", "RP": "red"},
            "Checked Num": {"FF": "blue", "RP": "red"},
            "Access Num": {"FF": "blue", "RP": "red"}
        }

        # Get the colors for the current measure
        type_colors = measure_colors.get(measure, {"FF": "blue", "RP": "green"})

        # Boolean flags to ensure each type appears only once in the legend
        added_labels = {"FF": False, "RP": False}
        
        # Plot bars for each group
        for group_name, group_data in query_data.groupby('Group'):
            bar_indices = [j for j, group in enumerate(query_data['Group']) if group == group_name]

            # Plot "Fully" bars
            if "FF" in group_data.columns:
                label = "FF" if not added_labels["FF"] else None
                ax.bar([x[idx] for idx in bar_indices], group_data['FF'], width=0.4, label=label, color=type_colors["FF"])
                added_labels["FF"] = True
                

            # Plot "Ranges" bars
            if "RP" in group_data.columns:
                label = "RP" if not added_labels["RP"] else None
                ax.bar([x[idx] + 0.4 for idx in bar_indices], group_data['RP'], width=0.4, label=label, color=type_colors["RP"])
                added_labels["RP"] = True

        # Add 'Combinations Num' text above the bars
        ax.set_xlabel('Number of Branches', fontsize=40)
        ax.set_xticks([pos + 0.2 for pos in x])
        ax.set_xticklabels(labels, rotation=70, ha='right', fontsize=30)

        ax.set_ylabel('Runtime (sec)' if measure == "Time" else             
        'NCE' if measure == "Checked Num" else 
        'NCA' if measure == "Access Num" else 
        measure, 
        fontsize=40
        )
        # Set y-axis to use scientific notation
        if measure == "Access Num":
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x*1e-8:.0f}$\\times10^8$' if x > 0 else '0'))
        else:
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x*1e-3:.0f}$\\times10^3$' if x > 0 else '0'))


        ax.tick_params(axis='y', labelsize=30)
        ax.legend(fontsize=30)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        output_file = os.path.join(file_path, f'comparison_fully_vs_ranges_{measure}_{dataName}_{factor_type}.pdf')
        plt.savefig(output_file)
        plt.show()
        print(f"Graph saved to: {output_file}") 

    def Generate_Time_vs_factors1(self, measure, factor_type):
        # Load the CSV file into a DataFrame
        file_path = f"/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/{factor_type}"
        file_path_csv = os.path.join(file_path, f'Run_info_ACSIncome_size50000_constraint3_{factor_type}1.csv')
        #file_path_csv = os.path.join(file_path, f'Run_info_TPC-H.csv')
        df = pd.read_csv(file_path_csv, sep=",")
        dataName = df['Data Name'][0]

        # Filter and clean the necessary columns
        df = df[['Query Num', factor_type, 'Type', measure]].dropna()

        # Pivot the data to prepare for plotting
        pivot_df = df.pivot_table(index=['Query Num', factor_type], columns='Type', values=measure, aggfunc='mean').reset_index()

        # Extract groups from BranchNum
        pivot_df['Group'] = pivot_df[factor_type]

        # Create a bar plot for the single Query Num
        query_num = pivot_df['Query Num'].iloc[0]  # Get the single query number
        query_data = pivot_df[pivot_df['Query Num'] == query_num]

        # Sort by Group and BranchNum
        query_data = query_data.sort_values(by=['Group', factor_type])

        # Extract unique x-axis values (data sizes)
        x_values = query_data[factor_type].astype(int).values  

        # Manually set x-tick positions for non-linear spacing
        x_positions = [1, 2, 5, 21, 51]  # Custom spacing (not equally spaced)

        # Mapping x_values to manually spaced x_positions
        x_mapping = dict(zip(x_values, x_positions))
        mapped_x_positions = [x_mapping[val] for val in x_values]

        # Set up figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Define color scheme for each measure
        measure_colors = {
            "Time": {"FF": "blue", "RP": "red"},
            "Checked Num": {"FF": "blue", "RP": "red"},
            "Access Num": {"FF": "blue", "RP": "red"}
        }
        type_colors = measure_colors.get(measure, {"FF": "blue", "RP": "green"})

        # Boolean flags to ensure each type appears only once in the legend
        added_labels = {"FF": False, "RP": False}

        # Plot bars for each group with non-linearly spaced x positions
        for group_name, group_data in query_data.groupby('Group'):
            bar_indices = [mapped_x_positions[j] for j, group in enumerate(query_data['Group']) if group == group_name]

            if "FF" in group_data.columns:
                label = "FF" if not added_labels["FF"] else None
                ax.bar(bar_indices, group_data['FF'], width=0.5, label=label, color=type_colors["FF"])
                added_labels["FF"] = True

            if "RP" in group_data.columns:
                label = "RP" if not added_labels["RP"] else None
                ax.bar(np.array(bar_indices) + 0.3, group_data['RP'], width=0.5, label=label, color=type_colors["RP"])
                added_labels["RP"] = True

        # Update x-axis to reflect custom spacing
        ax.set_xticks(x_positions)
        ax.set_xticklabels([f"{x//1000}K" for x in x_values], rotation=45, ha='right', fontsize=20)

        # Add x-axis break to visually indicate non-linearity
        ax.plot([2.2, 2.8], [-0.2, -0.2], transform=ax.transAxes, color='black', linewidth=1)  # Small break line

        ax.set_xlabel('Data Size', fontsize=25)
        ax.set_ylabel(
            'Runtime (sec)' if measure == "Time" else 
            'Number of \nCandidate Solutions \nChecked' if measure == "Checked Num" else 
            'Number of Clusters \nAccessed' if measure == "Access Num" else 
            measure, 
            fontsize=25
        )

        ax.tick_params(axis='y', labelsize=25)
        ax.legend(fontsize=20)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        output_file = os.path.join(file_path, f'comparison_fully_vs_ranges_{measure}_{dataName}_{factor_type}.pdf')
        plt.savefig(output_file)
        plt.show()
        print(f"Graph saved to: {output_file}")

    def Generate_Time_vs_DataSize(self, measure, factor_type, dataName):
        # Load the CSV file into a DataFrame
        file_path = f"/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/{factor_type}"
        file_path_csv = os.path.join(file_path, f'Run_info_TPC-H.csv')
        df = pd.read_csv(file_path_csv, sep=",")
        dataName = df['Data Name'][0]

        # Filter and clean the necessary columns
        df = df[['Query Num', factor_type, 'Type', measure]].dropna()

        # Pivot the data to prepare for plotting
        pivot_df = df.pivot_table(index=['Query Num', factor_type], columns='Type', values=measure, aggfunc='mean').reset_index()

        # Extract the numeric part from the factor_type and remove the 'K' or 'k'
        pivot_df['Group'] = pivot_df[factor_type].str.extract(r'(\d+)').astype(int)

        # Sort by the Group column (which is now numeric)
        pivot_df = pivot_df.sort_values(by='Group')

        # Create a bar plot for the single Query Num
        query_num = pivot_df['Query Num'].iloc[0]  # Get the single query number
        query_data = pivot_df[pivot_df['Query Num'] == query_num]

        # Set up figure
        fig, ax = plt.subplots(figsize=(10, 6), sharey=True)

        # Bar positions and labels
        x = range(len(query_data))
        labels = query_data[factor_type]

        # Define color scheme for each measure (each type gets a different shade)
        measure_colors = {
            "Time": {"FF": "blue", "RP": "red"},
            "Checked Num": {"FF": "blue", "RP": "red"},
            "Access Num": {"FF": "blue", "RP": "red"}
        }

        # Get the colors for the current measure
        type_colors = measure_colors.get(measure, {"FF": "blue", "RP": "green"})

        # Boolean flags to ensure each type appears only once in the legend
        added_labels = {"FF": False, "RP": False}

        # Plot bars for each group
        for group_name, group_data in query_data.groupby('Group'):
            bar_indices = [j for j, group in enumerate(query_data['Group']) if group == group_name]

            # Plot "Fully" bars
            if "FF" in group_data.columns:
                label = "FF" if not added_labels["FF"] else None
                ax.bar([x[idx] for idx in bar_indices], group_data['FF'], width=0.4, label=label, color=type_colors["FF"])
                added_labels["FF"] = True

            # Plot "Ranges" bars
            if "RP" in group_data.columns:
                label = "RP" if not added_labels["RP"] else None
                ax.bar([x[idx] + 0.4 for idx in bar_indices], group_data['RP'], width=0.4, label=label, color=type_colors["RP"])
                added_labels["RP"] = True

        # Add 'Combinations Num' text above the bars
        ax.set_xlabel('Data Size', fontsize=45)
        ax.set_xticks([pos + 0.2 for pos in x])
        
        # Apply the sorted labels to the x-axis, formatting the labels to add 'k'
        ax.set_xticklabels([f'{int(label.replace("K", "").replace("k", ""))}k' for label in labels], rotation=70, ha='right', fontsize=40)

        ax.set_ylabel('Runtime (sec)' if measure == "Time" else             
        'NCE' if measure == "Checked Num" else 
        'NCA' if measure == "Access Num" else 
        measure, 
        fontsize=44)
        if measure == "Time" or measure == "Checked Num":
            # Set y-axis to use scientific notation
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x*1e-3:.0f}$\\times10^3$' if x > 0 else '0'))
        else:
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x*1e-9:.0f}$\\times10^9$' if x > 0 else '0'))

        ax.tick_params(axis='y', labelsize=35)
        ax.legend(fontsize=30)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        output_file = os.path.join(file_path, f'comparison_fully_vs_ranges_{measure}_{dataName}_{factor_type}.pdf')
        plt.savefig(output_file)
        plt.show()
        print(f"Graph saved to: {output_file}")