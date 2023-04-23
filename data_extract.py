import glob, os
import pandas as pd

path = "./sim_runs"
all_files = glob.glob(os.path.join(path, "*_transaction_list.csv"))


print(all_files)

df_list = []

for file in all_files:
    df = pd.read_csv(file, index_col=None, header=0)
    df_list.append(df)

frame = pd.concat(df_list, axis=0, ignore_index=True)

frame.to_csv('./part2_submission/results.csv')
