import numpy as np
import pandas as pd
from scipy.stats import norm, uniform, expon, beta


class SyntheticDataGenerator:
    def __init__(self, seed=42):
        np.random.seed(seed)  # Set the random seed for reproducibility
        
    def generate_synthetic_data2(self, n_samples, attribute_specs=None, correlated_pairs=None, bins=None):
        """
        Generates synthetic integer data with specified attributes, distributions, and correlations for specified pairs.
        """
        attribute_names = list(attribute_specs.keys())
        synthetic_data = {}

        # Step 1: Generate independent data for attributes not in correlated pairs
        independent_attributes = set(attribute_names)
        for pair in correlated_pairs:
            independent_attributes -= set(pair[:2])

        for attr in independent_attributes:
            dist_type, low, high = attribute_specs[attr]
            synthetic_data[attr] = self.generate_attribute(n_samples, dist_type, low, high, bins)

        # Step 2: Generate correlated pairs
        for idx, (attr1, attr2, corr) in enumerate(correlated_pairs):
            # Handle correlated pairs separately
            print(f"Processing correlated pair: {attr1} with {attr2} (Correlation: {corr})")

            dist_type1, low1, high1 = attribute_specs[attr1]
            dist_type2, low2, high2 = attribute_specs[attr2]

            # Generate correlated normal data
            mean = [0, 0]
            cov = [[1, corr], [corr, 1]]
            base_data = np.random.multivariate_normal(mean, cov, n_samples)

            # Transform correlated normal data to specified distributions
            attr1_data = self.transform_to_distribution(base_data[:, 0], dist_type1, low1, high1, bins)
            attr2_data = self.transform_to_distribution(base_data[:, 1], dist_type2, low2, high2, bins)

            # If the attributes already exist, merge the correlated data with the existing data
            if attr1 in synthetic_data:
                synthetic_data[attr1] = (synthetic_data[attr1] + attr1_data) / 2  # Adjust merging logic if needed
            else:
                synthetic_data[attr1] = attr1_data

            if attr2 in synthetic_data:
                synthetic_data[attr2] = (synthetic_data[attr2] + attr2_data) / 2  # Adjust merging logic if needed
            else:
                synthetic_data[attr2] = attr2_data

        # Step 3: Convert to DataFrame and save
        df = pd.DataFrame(synthetic_data)
        file_path = 'synthetic_data_correlated.csv'
        df.to_csv(file_path, index=False)
        print(f"Synthetic integer data with specified correlations saved to {file_path}")
        return df, "synthetic_data", n_samples

    def generate_synthetic_data1(self, n_samples, attribute_specs=None, correlated_pairs=None, bins=None):
        """
        Generates synthetic integer data with specified attributes, distributions, and correlations for specified pairs.
        """
        attribute_names = list(attribute_specs.keys())
        synthetic_data = {}

        # Step 1: Generate independent data for attributes not in correlated pairs
        independent_attributes = set(attribute_names)
        for pair in correlated_pairs:
            independent_attributes -= set(pair[:2])

        for attr in independent_attributes:
            dist_type, low, high = attribute_specs[attr]
            synthetic_data[attr] = self.generate_attribute(n_samples, dist_type, low, high, bins)

        # Step 2: Generate correlated pairs
        for attr1, attr2, corr in correlated_pairs:
            if attr1 in synthetic_data or attr2 in synthetic_data:
                raise ValueError(f"Attributes '{attr1}' and '{attr2}' must be unique in correlated pairs.")
            
            dist_type1, low1, high1 = attribute_specs[attr1]
            dist_type2, low2, high2 = attribute_specs[attr2]

            # Generate correlated normal data
            mean = [0, 0]
            cov = [[1, corr], [corr, 1]]
            base_data = np.random.multivariate_normal(mean, cov, n_samples)

            # Transform correlated normal data to specified distributions
            synthetic_data[attr1] = self.transform_to_distribution(base_data[:, 0], dist_type1, low1, high1, bins)
            synthetic_data[attr2] = self.transform_to_distribution(base_data[:, 1], dist_type2, low2, high2, bins)

        # Step 3: Convert to DataFrame and save
        df = pd.DataFrame(synthetic_data)
        file_path = 'synthetic_data_correlated.csv'
        df.to_csv(file_path, index=False)
        print(f"Synthetic integer data with specified correlations saved to {file_path}")
        return df, "synthetic_data", n_samples

    def generate_attribute(self, n_samples, dist_type, low, high, bins=None):
        """Generate an independent attribute with consistent binning."""
        if dist_type == 'normal':
            data = norm.rvs(size=n_samples)
        elif dist_type == 'uniform':
            data = uniform.rvs(size=n_samples)
        elif dist_type == 'exponential':
            data = expon.rvs(size=n_samples)
        elif dist_type == 'beta':
            data = beta.rvs(2, 5, size=n_samples)
        else:
            raise ValueError("Supported distributions: 'normal', 'uniform', 'exponential', 'beta'")
        
        scaled_data = data * (high - low) + low

        # Apply consistent binning
        if bins and isinstance(bins, int):
            bin_edges = np.linspace(low, high, bins + 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            indices = np.digitize(scaled_data, bins=bin_edges) - 1
            indices = np.clip(indices, 0, bins - 1)  # Ensure indices are valid
            return bin_centers[indices].astype(int)

        return np.clip(np.round(scaled_data), low, high).astype(int)

    def transform_to_distribution(self, data, dist_type, low, high, bins=None):
        """Transform standard normal data to a specified distribution with consistent binning."""
        if dist_type == 'normal':
            transformed_data = norm.cdf(data) * (high - low) + low
        elif dist_type == 'uniform':
            transformed_data = uniform.cdf(data) * (high - low) + low
        elif dist_type == 'exponential':
            transformed_data = expon.ppf(norm.cdf(data)) * (high - low) + low
        elif dist_type == 'beta':
            transformed_data = beta.ppf(norm.cdf(data), a=2, b=5) * (high - low) + low
        else:
            raise ValueError("Supported distributions: 'normal', 'uniform', 'exponential', 'beta'")
        
        # Apply consistent binning
        if bins and isinstance(bins, int):
            bin_edges = np.linspace(low, high, bins + 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            indices = np.digitize(transformed_data, bins=bin_edges) - 1
            indices = np.clip(indices, 0, bins - 1)  # Ensure indices are valid
            return bin_centers[indices].astype(int)

        return np.clip(np.round(transformed_data), low, high).astype(int)

