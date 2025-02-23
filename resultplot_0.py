#!/usr/bin/python 
# -*- coding: utf-8 -*-
"""
 @Author: Jane
 @FileName: resultplot.py
 @DateTime: 2024/1/26 16:05
 @SoftWare: PyCharm
"""

import subprocess
import flopy
import re
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def extract_data_layer(filename, main_keyword1, main_keyword2, num_lines):
    data = []
    with open(filename, 'r') as file:
        content = file.read()

        # Find the index of main_keyword1
        start_index = content.find(main_keyword1)
        if start_index == -1:
            return data  # Keyword not found

        # Find the index of main_keyword2 after main_keyword1
        end_index = content.find(main_keyword2, start_index)
        if end_index == -1:
            return data  # Keyword not found

        # Extract the content between main_keyword2 and main_keyword1
        extracted_content = content[end_index + len(main_keyword2):].strip()

        # Split the content into lines
        lines = extracted_content.split('\n')

        # Process each line
        for line in lines[:num_lines]:
            # Extract numbers from the line using regular expression
            numbers = re.findall(r'\S+', line)

            # Filter out zeros and take only the first 10 non-zero numbers
            non_zero_numbers = [float(num) for num in numbers if num != '0']
            data.extend(non_zero_numbers[:10])

    return data


# 提取地层剖面Sn的函数
def extract_data_row(filename, main_keyword1, main_keyword2, num_lines):
    data = []
    with open(filename, 'r') as file:
        content = file.read()

        # Find the index of main_keyword1
        start_index = content.find(main_keyword1)
        if start_index == -1:
            return data  # Keyword not found

        # Find the index of main_keyword2 after main_keyword1
        end_index = content.find(main_keyword2, start_index)
        if end_index == -1:
            return data  # Keyword not found

        # Extract the content between main_keyword2 and main_keyword1
        extracted_content = content[end_index + len(main_keyword2):].strip()

        # Split the content into lines
        lines = extracted_content.split('\n')

        # Process each line
        for line in lines[:num_lines]:
            # Extract numbers from the line using regular expression
            numbers = re.findall(r'\S+', line)

            # 提取每行前多少位数，不过滤零
            data.extend([float(num) for num in numbers[:70]])

    return data


# path_record.txt 的内容，即将模型input路径赋给file_path
with open("path_record.txt", 'r') as record_file:
    file_path = record_file.read().strip()


# 绘制NAPL相饱和度平面X-Y分布
# 提取指定地层的Sn数据
def Sn_XY(lay):
    filename = os.path.join(os.path.dirname(file_path), "UTEX01.SATP")
    # 关键词1：提取结果所在的时间
    main_keyword1 = 'TIME =       30.000000 DAYS'  # 提取的是模拟的最终结果30d
    # 关键词2：提取对应相
    main_keyword2 = f'SAT. OF PHASE            2 IN LAYER            {lay}'
    # 确定提取关键词1、2之后的数据行数
    num_lines = 210
    result = extract_data_layer(filename, main_keyword1, main_keyword2, num_lines)

    # Reshape the data into a 30×70 array   长70宽30
    heatmap_data = np.array(result[:2100]).reshape((30, 70))  # (NY,NX)

    # Save the heatmap data to a text file
    heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_lay_{lay}.txt")
    np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')

    # 绘图显示平面X-YSn分布
    plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
    plt.colorbar(shrink=0.45)
    plt.title(f'Sn of DNAPLs in lay{lay}')
    plt.show()
    print(f"Heatmap data saved to {heatmap_filename}")


# # 运行Sn_XY(lay)
# lay = 1  # 注意，此处的层是读取文件里关键词，不需要从0开始计
# Sn_XY(lay)

# 绘制NAPL相饱和度剖面X-Z分布
# 基于PreProcess_Files2调取剖面数据，生成文件UTex01_XZ.MESH及UTex01_XZ.SATP
# 指定exe文件路径
exe_path1 = r'G:\UTCHEM\PreProcess_Files2.exe'

# 指定输入文件路径(HEAD和INPUT文件)
input_file_name = os.path.join(os.path.dirname(file_path), "UTex01.SATP")
mesh_file_name = os.path.join(os.path.dirname(file_path), "UTex01.MESH")

# 指定剖面参数X-Z or Y-Z
parameter = 'X-Z'

# 构建命令行参数列表
command = [exe_path1, input_file_name, mesh_file_name, parameter]

# 使用subprocess运行exe文件，并将命令行参数传递给它
try:
    subprocess.run(command, check=True)
    print(f'{exe_path1} 运行成功！')
except subprocess.CalledProcessError as e:
    print(f'运行 {exe_path1} 时发生错误：{e}')


# 此时得到UTex01_XZ.SATP，即NAPL相剖面分布情况，从该文件中调取对应位置剖面数据并绘图
def Sn_XZ(row):
    filename = os.path.join(os.path.dirname(file_path), "UTex01_XZ.SATP")
    # 关键词1：提取结果所在的时间
    main_keyword1 = 'TIME =       30.000000 DAYS'
    # 关键词2：提取对应相
    main_keyword2 = f'SAT. OF PHASE	2 	IN LAYER            {row}'
    # 确定提取关键词1、2之后的数据行数
    num_lines = 3
    result = extract_data_row(filename, main_keyword1, main_keyword2, num_lines)
    num = len(result)
    # print(num)
    # print(result)
    # Reshape the data
    heatmap_data = np.array(result[:210]).reshape((3, 70))  # (NZ,NX)

    # Save the heatmap data to a text file
    heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_row_{row}.txt")
    np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')

    # 绘图显示剖面X-ZSn分布
    plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
    plt.colorbar(shrink=0.45)
    plt.title(f'Sn of DNAPLs in row {row}')
    plt.show()
    print(f"Heatmap data saved to {heatmap_filename}")


# # 运行Sn_XZ(row)
# row = 16  # 注意，此处的层是读取文件里关键词，不需要从0开始计
# Sn_XZ(row)

# 绘制NAPL相饱和度剖面Y-Z分布
# 基于PreProcess_Files2调取剖面数据，生成文件UTex01_XZ.MESH及UTex01_XZ.SATP
# 指定exe文件路径
exe_path2 = r'G:\UTCHEM\PreProcess_Files2.exe'

# 指定输入文件路径(HEAD和INPUT文件)
input_file_name = os.path.join(os.path.dirname(file_path), "UTex01.SATP")
mesh_file_name = os.path.join(os.path.dirname(file_path), "UTex01.MESH")

# 指定剖面参数X-Z or Y-Z
parameter = 'Y-Z'

# 构建命令行参数列表
command = [exe_path2, input_file_name, mesh_file_name, parameter]

# 使用subprocess运行exe文件，并将命令行参数传递给它
try:
    subprocess.run(command, check=True)
    print(f'{exe_path2} 运行成功！')
except subprocess.CalledProcessError as e:
    print(f'运行 {exe_path2} 时发生错误：{e}')


# 此时得到UTex01_YZ.SATP，即NAPL相剖面分布情况，从该文件中调取对应位置剖面数据并绘图
def Sn_YZ(col):
    filename = os.path.join(os.path.dirname(file_path), "UTex01_YZ.SATP")
    # 关键词1：提取结果所在的时间
    main_keyword1 = 'TIME =       30.000000 DAYS'
    # 关键词2：提取对应相
    main_keyword2 = f'SAT. OF PHASE	2 	IN LAYER            {col}'
    # 确定提取关键词1、2之后的数据行数
    num_lines = 3
    result = extract_data_row(filename, main_keyword1, main_keyword2, num_lines)
    num = len(result)
    # print(num)
    # print(result)
    # Reshape the data into a 10×30 array   长30宽10
    heatmap_data = np.array(result[:90]).reshape((3, 30))  # (NZ,NY)

    # Save the heatmap data to a text file
    heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_col_{col}.txt")
    np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')

    # 绘图显示剖面Y-ZSn分布
    plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
    plt.colorbar(shrink=0.45)
    plt.title(f'Sn of DNAPLs in col {col}')
    plt.show()
    print(f"Heatmap data saved to {heatmap_filename}")


# # 运行Sn_YZ(col)
# col = 10  # 注意，此处的层是读取文件里关键词，不需要从0开始计
# Sn_YZ(col)


# 水头结果绘图
def head_plot(file_path):
    # 获取数据
    hds_file_path = os.path.join(os.path.dirname(file_path), "mymodel", "function_pyutchemflopy.hds")
    headobj = flopy.utils.binaryfile.HeadFile(hds_file_path)
    head = headobj.get_data()[2]  # 0：初始时刻水头，1，2对应应力期
    # 将水头数据保存至表格中
    df = pd.DataFrame(head)
    # df.to_csv(r".\mymodel\function_pyutchemflopy_H%s.csv" % i)  # i不影响水头结果
    df.to_csv(r".\mymodel\function_pyutchemflopy_H.csv")

    # 水头分布图
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_subplot(1, 2, 1)
    head_p = ax1.imshow(head)
    plt.title('Head (m)')
    plt.colorbar(head_p, fraction=0.05, pad=0.05, shrink=0.3)
    plt.show()


# # 运行head_plot
# head_plot(file_path)

# 污染浓度结果绘图
conc = flopy.utils.UcnFile('./mymodel/MT3D001.UCN')
times = conc.get_times()
conc = conc.get_alldata()
conc = np.array(conc)


# print(conc.shape)


# 对应最终timprs的平面X-Y浓度分布绘图
def conc_XY(lay, conc):
    fig = plt.figure(figsize=(15, 60))
    num_timprs = 3  # timprs最大时，绘制模拟最终结果的图

    df = pd.DataFrame(conc[num_timprs, lay])
    output_folder = os.path.join(".", "mymodel")
    os.makedirs(output_folder, exist_ok=True)
    csv_file_path = os.path.join(output_folder, f"function_pyutchemflopy_C_layer{lay}.csv")
    df.to_csv(csv_file_path, index=False)

    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(conc[num_timprs, lay], cmap='Spectral_r')
    plt.show()


# # 运行concentration_XY
# lay = 0
# conc_XY(lay, conc)


# 对应最终timprs的剖面X-Z浓度分布绘图
def conc_XZ(row, conc):
    fig = plt.figure(figsize=(15, 60))
    num_timprs = 3  # timprs最大时，绘制模拟最终结果的图

    df = pd.DataFrame(conc[num_timprs, :, row, :])  # [timprs, nlay, nrow, ncol ]
    output_folder = os.path.join(".", "mymodel")
    os.makedirs(output_folder, exist_ok=True)
    csv_file_path = os.path.join(output_folder, f"function_pyutchemflopy_C_layer{row}.csv")
    df.to_csv(csv_file_path, index=False)

    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(conc[num_timprs, :, row], cmap='Spectral_r')  # 注意对于X-Z，conc[num_timprs, :, row]
    plt.show()


# # 运行concentration_XZ
# row = 15
# conc_XZ(row, conc)


# 对应最终timprs的剖面Y-Z浓度分布绘图
def conc_YZ(col, conc):
    fig = plt.figure(figsize=(15, 60))
    num_timprs = 3  # timprs最大时，绘制模拟最终结果的图

    df = pd.DataFrame(conc[num_timprs, :, :, col])  # [timprs, nlay, nrow, ncol ]
    output_folder = os.path.join(".", "mymodel")
    os.makedirs(output_folder, exist_ok=True)
    csv_file_path = os.path.join(output_folder, f"function_pyutchemflopy_C_layer{col}.csv")
    df.to_csv(csv_file_path, index=False)

    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(conc[num_timprs, :, :, col], cmap='Spectral_r')  # 注意对于X-Z，conc[num_timprs, :, :, col]
    plt.show()

# # 运行concentration_YZ
# col = 15
# conc_YZ(col, conc)
