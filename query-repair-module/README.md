📊 Efficient Query Repair for Aggregate Constraints

📄 Abstract

Query Repair for Aggregate Constraints introduces multiple algorithms designed to handle diverse datasets effectively.

⚙️ Algorithms

This project implements three algorithms for query repair:

Brute Force Algorithm

To test this algorithm, remove the comment in main.py.

Full Cluster Filtering Algorithm (FF)

Cluster Range Pruning Algorithm (RP)

📂 Datasets

The project includes three datasets located in the Datasets folder:

ACSIncome

Healthcare

TPCH

🔧 Dataset Configuration

Edit each dataset's path in the Dataframe.py file to match your directory structure.

🚀 How to Run Experiments

To run the experiments, follow these steps:

Set Configuration:

In main.py, specify parameters such as:

dataName

dataSize

QueryNumber

And other required configurations.

Output Directory:

Set the outputDirectory where results will be saved. This folder will contain:

The output of each algorithm.

A summary table consolidating the results.

Run the Experiment:

Execute the following command:

python main.py

📜 Where to Find the Paper

The technical report is available in the extended version. For further details, please refer to the report.

✅ For any questions or contributions, feel free to reach out!

