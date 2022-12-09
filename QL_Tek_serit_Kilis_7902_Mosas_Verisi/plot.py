import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
def plot(csv_name):
    col_list = ["step_time", "total_wait_time"]
    df = pd.read_csv(csv_name, usecols=col_list)
    # same plotting code as above!
    sns.lineplot(df["step_time"],df["total_wait_time"])
    plt.show()
    
    #print(df["step_time"])

plot("2022_06_21_13_35_41_alpha0.1_gamma0.99_eps0.05_decay1.0_conn0_run1.csv")
