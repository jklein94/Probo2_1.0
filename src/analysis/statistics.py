"""Statistics module"""


import pandas as pd
from sqlalchemy.sql import functions



def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """[summary]

    Args:
        df (pd.DataFrame): [description]

    Returns:
        pd.DataFrame: [description]
    """
    calculate_cols = [
        'id', 'solver_id', 'anon_1', 'instance', 'solver_format', 'runtime',
       'task_id', 'symbol', 'cut_off', 'timed_out',
       'exit_with_error', 'error_code', 'additional_argument', 'benchmark_id',
        'validated', 'benchmark_name', 'tag','correct_solved', 'incorrect_solved', 'no_reference','correct'
    ]
    return (df[calculate_cols]
            .rename(columns={
        "anon_1": "solver_full_name",
        "symbol": "task"
     }).astype({
         'solver_id': 'int16',
         'benchmark_id': 'int16',
        'task_id': 'int8',
         'cut_off': 'int16',
         'runtime': 'float32',
         'instance': 'str',
         'solver_format': 'str',
         'task': 'str',
         'tag': 'str',
        'benchmark_name': 'str',
        'correct_solved': 'bool', 'incorrect_solved': 'bool', 'no_reference': 'bool'
    })
    )

def get_task_summary(df: pd.DataFrame, summary_dict):
    task = df.task.iloc[0]
    benchmark= df.benchmark_name.iloc[0]
    functions_to_call = ['sum','min','max','mean','num_solved','num_timed_out','num_exit_with_error','coverage']
    stats_solver = (df
                .groupby(["solver_id"],as_index=False)
                .apply(lambda df: dispatch_function(df,functions_to_call,par_penalty=0))
                )
    stats_summary = dispatch_function(df,functions_to_call)
    summary_dict[benchmark][task] = {'summary': stats_summary, 'solver': stats_solver}


def get_experiment_summary_as_string(df: pd.DataFrame) -> str:
    tag = df.tag.iloc[0]
    tasks_str = ",".join(list(df.task.unique()))
    solvers_str = ",".join(list(df.solver_full_name.unique()))
    benchmarks_str = ",".join(list(df.benchmark_name.unique()))
    unique_instances_str = len(list(df.instance.unique()))
    final_string =f'+++++SUMMARY+++++\nTag: {tag}\nBenchmarks: {benchmarks_str}\n#Unique Instances: {unique_instances_str}\nTasks: {tasks_str}\nSolvers: {solvers_str}\n\n'
    summary_dict = dict()
    for benchmark in list(df.benchmark_name.unique()):
        summary_dict[benchmark] = dict()
    df.groupby(['benchmark_id','task_id'],as_index=False).apply(lambda df: get_task_summary(df,summary_dict))
    for benchmark, summary_tasks in summary_dict.items():
        benchmark_sum_str =f'#####{benchmark}#####\n\n'
        for task,task_summary in summary_tasks.items():
            task_sum_str = f'*****{task}*****\n\n'
            summary = task_summary['summary']
            solver = task_summary['solver']
            summary_str = (f'Solver: {summary.solver}\n#Solved: {summary.num_solved}\n#Timeout: {summary.num_timed_out}\n#Errors: {summary.num_exit_with_error}\nCoverage: {summary.coverage}%\n\n')
            task_sum_str += summary_str
            solver_sum_str =""
            for index, row in solver.iterrows():
                sum_runtime = row['sum']
                mean_runtime = row['mean']
                min_runtime = row['min']
                max_runtime = row['max']
                cur_solver = f'-----{row.solver}-----\n#Solved: {row.num_solved}\n#Timeout: {row.num_timed_out}\n#Errors: {row.num_exit_with_error}\nCoverage: {row.coverage}%\nTotal runtime: {sum_runtime}\nMean runtime: {mean_runtime}\nMin runtime: {min_runtime}\nMax runtime: {max_runtime}\n\n'
                solver_sum_str += cur_solver

            benchmark_sum_str += task_sum_str + solver_sum_str
    return final_string + benchmark_sum_str


def get_info_as_strings(df: pd.DataFrame) -> dict:
    tags = ",".join(df.tag.unique())
    solvers = ",".join(df.solver_full_name.unique())
    tasks = ",".join(df.task.unique())
    benchmarks = ",".join(df.benchmark_name.unique())
    return {'tag': tags,'solver': solvers, 'task': tasks,'benchmark': benchmarks}

def sum_runtimes(df):
    return df.runtime.sum()

def mean_runtimes(df):
    return df.runtime.mean()

def min_runtimes(df):
    return df.runtime.min()

def max_runtimes(df):
    return df.runtime.max()
def sum_timed_out(df):
    return df.timed_out.sum()
def sum_exit_with_error(df):
    return df.exit_with_error.sum()
def var_runtimes(df):
    return df.runtime.var()
def median_runtimes(df):
    return df.runtime.median()
def std_runtimes(df):
    return df.runtime.std()

def coverage(df):
    total = df.instance.shape[0]
    solved =num_solved(df)
    return solved / total * 100

def penalised_average_runtime(df, penalty):
    cut_off = df.cut_off.iloc[0]
    solved_instances = df[(df.timed_out == False)&(df.exit_with_error == False)]
    solved_runtime = solved_instances.runtime.values.sum()
    total_num = df.shape[0]
    solved_num = solved_instances.shape[0]
    unsolved_num =  total_num - solved_num
    unsolved_runtime = unsolved_num * cut_off * penalty
    return (solved_runtime + unsolved_runtime) / total_num

def num_solved(df):
    total = df.instance.shape[0]
    return total -(sum_timed_out(df) + sum_exit_with_error(df))


def dispatch_function(df,functions,par_penalty=10):

    dispatch_map = {'mean':mean_runtimes(df),
                    'sum': sum_runtimes(df),
                    'min':min_runtimes(df),
                    'max':max_runtimes(df),
                    'median':median_runtimes(df),
                    'var': var_runtimes(df),
                    'std': std_runtimes(df),
                    f'PAR{par_penalty}': penalised_average_runtime(df,par_penalty),
                    'coverage': coverage(df),
                    'num_timed_out': sum_timed_out(df),
                    'num_exit_with_error': sum_exit_with_error(df),
                    'num_solved': num_solved(df)
    }
    functions_to_call = {key: dispatch_map[key] for key in functions}
    info = get_info_as_strings(df)
    ser_dict = dict(info,**functions_to_call)
    return pd.Series(ser_dict)

def merge_dataframes(data_frames, on):
    """[summary]

    Args:
        data_frames ([type]): [description]
        on ([type]): [description]

    Returns:
        [type]: [description]
    """
    df = data_frames[0]
    for df_ in data_frames[1:]:
        df = df.merge(df_, on=on)
    return df

def create_vbs(df,vbs_id):


    best_runtime = df['runtime'].min()


    row = df.iloc[0]
    row['solver_id'] = vbs_id
    row['solver_full_name'] = "vbs"
    row['id'] = -1
    row['runtime'] = best_runtime
    row['validated'] = True
    row['correct_solved'] = True
    row['correct'] = 'correct'
    if  pd.isna(best_runtime):
        row['timed_out'] = True
    else:
        row['timed_out'] = False


    return row

# def calculate_iccma_scores(df: pd.DataFrame, grouping: list) -> pd.DataFrame:
#     """[summary]

#     Args:
#         df (pd.DataFrame): [description]
#         grouping (list): [description]

#     Returns:
#         pd.DataFrame: [description]
#     """
#     return (df
#             .groupby(grouping,as_index=False)
#             .apply(lambda group: calculate_iccma_score(group))
#             )
# def calculate_iccma_score(df: pd.DataFrame)-> pd.Series:
#     """[summary]

#     Args:
#         df (pd.DataFrame): [description]

#     Returns:
#         : [description]
#     """

#     info = get_info_as_strings(df)
#     iccma_score = df[(df['timed_out'] == False)
#                 & (df['exit_with_error'] == False) & (df.validated == True) & (df.correct_solved == True)].shape[0]
#     print(df['solver_full_name'].iloc[0],iccma_score)
#     info['iccma_score'] = iccma_score
#     return pd.Series(info)




