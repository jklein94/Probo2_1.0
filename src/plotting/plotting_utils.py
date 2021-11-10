import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from src.plotting import CactusPlot, ScatterPlot
from src.analysis.statistics import get_info_as_strings
def create_file_name(df: pd.DataFrame,info,save_to: str,kind: str) -> str:
    task_symbol = info['task']
    benchmark_name = info['benchmark']
    curr_tag = info['tag']
    return os.path.join(save_to, "{}_{}_{}_{}".format(task_symbol, benchmark_name,curr_tag,kind))

def prepare_data_cactus_plot(df: pd.DataFrame):
    return (df
     .groupby(['tag','task_id','benchmark_id','solver_id'])
     .apply(lambda g: g.assign(rank=g['runtime'].rank(method='dense',ascending=True)))
     .droplevel(0)
     .reset_index(drop=True)
     .groupby(['tag','task_id','benchmark_id'])
     )
def prep_catus_plot(df: pd.DataFrame)  -> pd.DataFrame:
    plot_grouping = ['tag','task_id','benchmark_id','solver_id']
    return (df.rename(columns={"anon_1": "solver_full_name","symbol": "task"})
            .astype({'solver_id': 'int16','benchmark_id': 'int16','task_id': 'int8','cut_off': 'int16', 'runtime': 'float32'})
            .groupby(plot_grouping,as_index=False)
            .apply(lambda df: df.assign(rank=df['runtime'].rank(method='dense',ascending=True))))
def prepare_grid(df: pd.DataFrame)-> pd.DataFrame:
    return (df
            .groupby(['tag','task_id','benchmark_id','solver_id'],as_index=False)
            .apply(lambda g: g.assign(rank=g['runtime'].rank(method='dense',ascending=True)))
            .droplevel(0)
            .reset_index(drop=True)
          )



def get_overlapping_instances(df,solver_id):
    solver_df = df[df.solver_id.isin(solver_id)]
    unique_instances = solver_df.groupby('solver_id').apply(lambda solver: set(solver[~(solver.runtime.isnull())]['instance'].unique())).tolist()
    overlapping = list(set.intersection(*unique_instances))
    return solver_df[solver_df.instance.isin(overlapping)]

def prep_scatter_data(df):
    overlapping_instances_df = get_overlapping_instances(df)
    unique_solvers = list(overlapping_instances_df.solver.unique())
    runtimes_solver = dict()
    for s in unique_solvers:
        runtimes_solver[s]  = overlapping_instances_df[overlapping_instances_df.solver == s].sort_values('instance')['runtime'].values

    return pd.DataFrame.from_dict(runtimes_solver).fillna(0)
def scatter_plot(df: pd.DataFrame, save_to: str, options: dict, grouping: list):
    pass
def create_scatter_plot(df: pd.DataFrame, save_to: str, options: dict)->str:
    info = get_info_as_strings(df)
    df['Solver'] = df['solver_full_name']
    options['title'] = info['task'] + " " + info['benchmark']
    save_file_name = create_file_name(df,info,save_to,'cactus')
    options['save_to'] = save_file_name
    ScatterPlot.Scatter(options).create(df)
    return save_file_name

def cactus_plot(df, save_to, options,grouping):
    ranked = (df.groupby(grouping,as_index=False)
                    .apply(lambda df: df.assign(rank=df['runtime'].rank(method='dense',ascending=True))))
    plot_grouping = grouping.copy()
    plot_grouping.remove('solver_id')
    return ranked.groupby(plot_grouping).apply(lambda df: create_cactus_plot(df,save_to,options))

def create_cactus_plot(df,save_to,options):
    info = get_info_as_strings(df)
    df['Solver'] = df['solver_full_name']
    options['title'] = info['task'] + " " + info['benchmark']
    save_file_name = create_file_name(df,info,save_to,'cactus')
    options['save_to'] = save_file_name
    CactusPlot.Cactus(options).create(df)
    return save_file_name

def prep_data_count_plot(df):
    conds = [((df.timed_out == False) & (df.exit_with_error == False)),df.timed_out == True,df.exit_with_error == True]
    choices = ['Solved','Timed out','Aborted']
    df['Status'] = np.select(conds,choices)
    return df

def create_count_plot(df, save_to, options):
    info = get_info_as_strings(df)
    save_file_name = create_file_name(df,info,save_to,'count')
    ax = sns.countplot(data=df,x='solver_full_name',hue='Status')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    benchmark_name = info['benchmark']
    task = info['task']
    ax.set_title(f'{benchmark_name} {task}')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    figure = ax.get_figure()
    figure.savefig(f"{save_file_name}.png",
                   bbox_inches='tight',
                   transparent=True)
    plt.clf()
    return save_file_name


def count_plot(df,save_to,options,grouping):
    preped_data = df.groupby(grouping,as_index=False).apply(lambda df: prep_data_count_plot(df))
    plot_grouping = grouping.copy()
    plot_grouping.remove('solver_id')
    return preped_data.groupby(plot_grouping).apply(lambda df: create_count_plot(df,save_to,options))

def create_pie_chart(df: pd.DataFrame,save_to: str, options: dict):
    pass

def pie_chart(df: pd.DataFrame, save_to: str, options: dict, grouping: list):
    pass
def dispatch_function(df,functions,save_to,options,grouping):
    only_solved_mask = (df.timed_out == False) & (df.exit_with_error == False)
    dispatch_map = {'cactus':cactus_plot(df[only_solved_mask],save_to,options,grouping),
                    'count':count_plot(df,save_to,options,grouping)

    }
    functions_to_call = {key: dispatch_map[key] for key in functions}
    return pd.Series(functions_to_call)