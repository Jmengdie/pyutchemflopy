#!/usr/bin/python 
# -*- coding: utf-8 -*-
"""
 @Author: Jane
 @FileName: 遗传算法.py
 @DateTime: 2023/11/10 15:05
 @SoftWare: PyCharm
"""

import numpy as np
from function_ND import function_ND
from geneticalgorithm import geneticalgorithm as ga

# 创建一个空列表用于存储每次迭代的结果
iteration_results = []


def objective_function(params):
    P0, P1, P2 = params
    C = function_ND(P0, P1, P2)
    C1 = C[0]
    C2 = C[1]
    C3 = C[2]
    # C4 = C[3]
    target_values = np.array([C1, C2, C3])
    reference_values = np.array([1460, 47.4, 48.6])  # 期望的目标值,此处为2022年采样检测值
    RMSE = np.sqrt(((target_values - reference_values) ** 2).mean())  # 计算均方差

    # 将当前参数和RMSE存储到全局变量中
    iteration_results.append((P0, P1, P2, RMSE))

    return RMSE


algorithm_parameters = {'max_num_iteration': 50,  # max_num_iteration:100-500
                        'population_size': 10,  # population_size:50-200
                        'mutation_probability': 0.02,  # mutation_probability:0.01-0.1
                        'elit_ratio': 0.01,  # elit_ratio:0.01-0.1
                        'crossover_probability': 0.6,  # crossover_probability:0.5-0.9
                        'parents_portion': 0.3,  # parents_portion:0.2-0.5
                        'crossover_type': 'uniform',
                        'max_iteration_without_improv': None}

# 通过手动打印在每次迭代时输出结果
model = ga(function=objective_function,
           dimension=3,
           variable_type_mixed=np.array(['real', 'real', 'real']),
           variable_boundaries=np.array([[7E-7, 8E-7], [10E-6, 10], [0.1, 30]]),
           algorithm_parameters=algorithm_parameters,
           convergence_curve=False,
           function_timeout=120)

# 运行遗传算法
model.run()

# 输出最优解
print('最优解:')
print(f"D:{model.output_dict['variable'][0]}")
print(f"L:{model.output_dict['variable'][1]}")
print(f"αL:{model.output_dict['variable'][2]}")

# 在每次迭代结束后逐步输出当前结果
for i, (P0, P1, P2, RMSE) in enumerate(iteration_results):
    print(f"Iteration {i + 1}: P0={P0}, P1={P1}, P1={P2},RMSE={RMSE}")

# 将所有迭代结果保存到 txt 文件中
with open("iteration_results.txt", "w") as f:

    for i, (P0, P1, P2, RMSE) in enumerate(iteration_results):
        f.write(f"Iteration {i + 1}: P0={P0}, P1={P1}, P2={P2}, RMSE={RMSE}\n")

print("所有迭代结果已保存到 iteration_results.txt 文件中。")
