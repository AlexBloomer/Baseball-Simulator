import pickle
import pandas as pd

# Load the pickle file
with open('team_cache.pkl', 'rb') as f:
    data = pickle.load(f)

# Convert the data to a DataFrame (assuming it's dictionary-like)
df = pd.DataFrame.from_dict(data, orient='index')

# Save as CSV
df.to_csv('team_cache.csv')

print("Conversion complete: team_cache.csv")
