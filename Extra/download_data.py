import kagglehub

# Download first dataset (already done but ensuring we have the path)
path1 = kagglehub.dataset_download("thammuio/all-agriculture-related-datasets-for-india")
print("Path to dataset 1:", path1)

# Download second dataset
path2 = kagglehub.dataset_download("akshatgupta7/crop-yield-in-indian-states-dataset")
print("Path to dataset 2:", path2)
