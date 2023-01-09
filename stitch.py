import pandas as pd
from pathlib import Path


def stitch():

    combined_df = []

    file_dir = Path(__file__).parent / 'states'

    for file in file_dir.glob('*'):
        
        temp_df = pd.read_csv(file)

        combined_df.append(temp_df)

    pd.concat(combined_df).to_csv('all_names.csv', index = False)



if __name__ == "__main__":
    stitch()
