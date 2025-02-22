#!/usr/bin/python 
# -*- coding: utf-8 -*-
"""
 @Author: Jane
 @FileName: pyutchem.py
 @DateTime: 2023/12/4 14:47
 @SoftWare: PyCharm
"""
# 在pyutchemflopy3的基础上，优化传质过程，使之能够扩散至Sn=0的区域

import subprocess
import flopy
import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil

config = {
    'font.family': 'Times New Roman',
    'font.size': 15,
    'font.serif': ['SimSun'],
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'mathtext.fontset': 'stix',
    'savefig.dpi': 300, }
plt.rcParams.update(config)

# # 第一部分：运行UTCHEM程序
# # 指定exe文件路径
# exe_path = r'G:\UTCHEM\utchem93.exe'
# # 指定保存生成文件的目录
# output_dir = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3'
#
# # # 第一阶段
# # # 指定输入文件路径(HEAD和INPUT文件)
# head_path = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\head'
# input_path = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\input'
#
# # 如果输出目录不存在，则创建该目录
# os.makedirs(output_dir, exist_ok=True)
#
# # 读取输入文件1(HEAD)的内容
# with open(head_path, 'r') as input_file1:
#     input_content1 = input_file1.read()
#
# # 读取输入文件2(INPUT)的内容
# with open(input_path, 'r') as input_file2:
#     input_content2 = input_file2.read()
#
# # 使用subprocess运行exe文件，并将两个输入文件的内容传递给它
# try:
#     subprocess.run([exe_path], input=(input_content1 + input_content2).encode(), cwd=output_dir, check=True)
#     print(f'{exe_path} 运行成功！生成的文件保存到 {output_dir}')
# except subprocess.CalledProcessError as e:
#     print(f'运行 {exe_path} 时发生错误：{e}')

#
# # 修改RESTAR文件名称，为第二阶段模拟做准备
# # 定义文件路径
# old_file_path = r"H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test\utchem\UTex21.RESTAR"
# new_file_path = r"H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test\utchem\input2"
#
# # 如果目标文件已存在，则先删除
# if os.path.exists(new_file_path):
#     os.remove(new_file_path)
#
# # 重命名并覆盖文件
# shutil.move(old_file_path, new_file_path)
#
# print(f"文件已成功重命名并覆盖为 {new_file_path}")

# # 第二阶段
# # 指定输入文件路径(input2和infile文件)
# infile_path = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test2\utchem\infile'
# input2_path = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test\utchem\input2'
#
# # 读取输入文件3(infile)的内容
# with open(infile_path, 'r') as input_file3:
#     input_content3 = input_file3.read()
#
# # 使用 subprocess 运行 UTCHEM 程序，传递 infile 和 input2 的路径
# try:
#     # 将 input_file4_path 作为命令行参数传递，而不是读取内容
#     result = subprocess.run([exe_path], input=input_content1 + input_content3, cwd=output_dir, text=True, check=True)
#     print(f'{exe_path} 运行成功！生成的文件保存到 {output_dir}')
# except subprocess.CalledProcessError as e:
#     print(f'运行 {exe_path} 时发生错误：{e}')


# 第二部分：提取UTCHEM模拟数据及绘图
# 地层平面
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


# # extract the data of Sn in specific layer
# # i表示地层数
# for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
#     filename = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\UTex21.SATP'
#     # 关键词1：提取结果所在的时间
#     main_keyword1 = 'TIME =     1830'
#     # 关键词2：提取对应相
#     main_keyword2 = f'SAT. OF PHASE            2 IN LAYER            {i}'
#     # 确定提取关键词1、2之后的数据行数
#     num_lines = 195
#     result = extract_data_layer(filename, main_keyword1, main_keyword2, num_lines)
#
#     # Reshape the data into a 39×50 array
#     heatmap_data = np.array(result[:1950]).reshape((39, 50))  # (NY,NX)
#
#     # Save the heatmap data to a text file
#     heatmap_filename = fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\Sn_lay_{i}.txt'
#     np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')
#
#     # 对应每一个地层平面绘图
#     plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
#     plt.colorbar(shrink=0.45)
#     plt.title(f'Sn of DNAPLs in lay{i}')
#     plt.show()
#     print(f"Heatmap data saved to {heatmap_filename}")

# # 竖直剖面
# # 基于PreProcess_Files2调取剖面数据，生成文件UTex01_XZ.MESH及UTex01_XZ.SATP
# # 指定exe文件路径
# exe_path1 = r'G:\UTCHEM\PreProcess_Files2.exe'
#
# # 指定输入文件路径(HEAD和INPUT文件)
# input_file_name = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\UTex21.SATP'
# mesh_file_name = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\UTex21.MESH'
#
# # 指定剖面参数X-Z or Y-Z
# parameter = 'X-Z'
#
# # 构建命令行参数列表
# command = [exe_path1, input_file_name, mesh_file_name, parameter]
#
# # 使用subprocess运行exe文件，并将命令行参数传递给它
# try:
#     subprocess.run(command, check=True)
#     print(f'{exe_path1} 运行成功！')
# except subprocess.CalledProcessError as e:
#     print(f'运行 {exe_path1} 时发生错误：{e}')

# # 此时得到UTex01_XZ.SATP，即NAPL相剖面分布情况，从该文件中调取对应位置剖面数据并绘图
# # i表示行数
# for i in [20, 25, 30]:
#     filename = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\UTex21_XZ.SATP'
#     # 关键词1：提取结果所在的时间
#     main_keyword1 = 'TIME =     1710'
#     # 关键词2：提取对应相
#     main_keyword2 = f'SAT. OF PHASE	2 	IN LAYER            {i}'
#     # 确定提取关键词1、2之后的数据行数(应该和底层数是一致的)
#     num_lines = 9
#     result = extract_data_row(filename, main_keyword1, main_keyword2, num_lines)
#     num = len(result)
#     print(num)
#     print(result)
#     # Reshape the data into a 9×50 array
#     heatmap_data = np.array(result[:450]).reshape((9, 50))  # (NY,NX)
#
#     # Save the heatmap data to a text file
#     heatmap_filename = fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\Sn_row_{i}.txt'
#     np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')
#
#     # 对应每一个地层剖面绘图
#     plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
#     plt.colorbar(shrink=0.45)
#     plt.title(f'Sn of DNAPLs in row{i}')
#     plt.show()
#     print(f"Heatmap data saved to {heatmap_filename}")

# # 指定剖面参数X-Z or Y-Z
# parameter = 'Y-Z'
#
# # 构建命令行参数列表
# command = [exe_path1, input_file_name, mesh_file_name, parameter]
#
# # 使用subprocess运行exe文件，并将命令行参数传递给它
# try:
#     subprocess.run(command, check=True)
#     print(f'{exe_path1} 运行成功！')
# except subprocess.CalledProcessError as e:
#     print(f'运行 {exe_path1} 时发生错误：{e}')
#
# # 此时得到UTex01_YZ.SATP，即NAPL相剖面分布情况，从该文件中调取对应位置剖面数据并绘图
# # i表示行数
# for i in [20, 25, 30]:
#     filename = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\UTex21_YZ.SATP'
#     # 关键词1：提取结果所在的时间
#     main_keyword1 = 'TIME =     1710'
#     # 关键词2：提取对应相
#     main_keyword2 = f'SAT. OF PHASE	2 	IN LAYER            {i}'
#     # 确定提取关键词1、2之后的数据行数(应该和底层数是一致的)
#     num_lines = 9
#     result = extract_data_row(filename, main_keyword1, main_keyword2, num_lines)
#     num = len(result)
#     print(num)
#     print(result)
#     # Reshape the data into a 9×50 array
#     heatmap_data = np.array(result[:351]).reshape((9, 39))  # (NY,NX)
#
#     # Save the heatmap data to a text file
#     heatmap_filename = fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\Sn_col_{i}.txt'
#     np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')
#
#     # 对应每一个地层剖面绘图
#     plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
#     plt.colorbar(shrink=0.45)
#     plt.title(f'Sn of DNAPLs in row{i}')
#     plt.show()
#     print(f"Heatmap data saved to {heatmap_filename}")

# 第三部分：耦合flopy
modelname = "Jiading_test"  # 模型名称
mf = flopy.modflow.Modflow(modelname, exe_name="mf2005", namefile_ext='nam', model_ws='./mymodel', version='mf2005')
# 生成 mymodel 文件夹和 *.nam 文件

# 网格信息及其离散化(DIS)
Lx = 100.0  # x方向上长度
Ly = 78.0  # y方向上长度
nrow = 39  # 网格行数
ncol = 50  # 网格列数
delr = Lx / ncol  # x方向步长
delc = Ly / nrow  # y方向步长

nlay = 9  # 含水层数量
ztop = 4 * np.ones((nrow, ncol), dtype=np.float32)  # 垂直方向18m，假设顶部高程4m
zbotm = np.ones((nlay, nrow, ncol), dtype=np.float32)
zbotm[0, :, :] = 2
zbotm[1, :, :] = 0
zbotm[2, :, :] = -2
zbotm[3, :, :] = -4
zbotm[4, :, :] = -6
zbotm[5, :, :] = -8
zbotm[6, :, :] = -10
zbotm[7, :, :] = -12
zbotm[8, :, :] = -14

# 时间上划分(DIS)
nper = 3  # 应力期个数
steady = [True, False, False]  # 设置每个应力周期是否为稳定流，第一个应力期设置为稳定流，以创建初始水头便于后续模拟
perlen = [50, 3600, 2190]  # 应力期长度，稳定流为任意值，非稳定流不同数值代表天数
nstp = [50, 360, 219]  # 每个应力期的时间步数，如100意为将一个应力期的100天划分为100次
# step_interval_output = 2  # output will be saved every # of intervals
dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr,
                               delc=delc, top=ztop, botm=zbotm,
                               nper=nper, perlen=perlen, nstp=nstp, steady=steady)
# 生成了输出文件中的 *.dis 文件

# 设置含水层特征(LPF)
# 此处含水层由于DNAPLs自由相的存在，导致渗透系数发生变化，需根据DNAPLs饱和度分布进行换算，𝐾_𝑒𝑓𝑓=𝐾_𝑖*((1−𝑆_𝑁−𝑆_𝑟𝑤)/(1−𝑆_𝑟𝑤 ))^((2+3r_𝑏)/r_𝑏 )
laytyp = 1  # 含水层类型,>0潜水含水层，=0承压含水层，<0可变
Ki = np.ones((nlay, nrow, ncol), dtype=np.float64)  # 固有渗透系数，单位𝑚/𝑑
Ki[0, :, :] = 1.39E-02
Ki[1, :, :] = 1.39E-02
Ki[2, :, :] = 7.64E-01
Ki[3, :, :] = 7.64E-01
Ki[4, :, :] = 7.64E-01
Ki[5, :, :] = 8.60E-03
Ki[6, :, :] = 8.60E-03
Ki[7, :, :] = 1.57E-03
Ki[8, :, :] = 1.57E-03
Srw = 0.2
r = 2.0
# 计算每一层对应的Keff
hk = np.ones((nlay, nrow, ncol), dtype=np.float64)  # 水平渗透系数，单位：m/d
for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
    Sn = np.loadtxt(fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\Sn_lay_{i}.txt')
    hk[i - 1, :, :] = Ki[i - 1, :, :] * ((1 - Sn - Srw) / (1 - Srw)) ** ((2 + 3 * r) / r)
    hk_path = fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\hk{i}.txt'
    np.savetxt(hk_path, hk[i - 1, :, :])
vka = np.ones((nlay, nrow, ncol), dtype=np.float64)  # 垂直渗透系数，单位：m/d,当layvka≠0时，表示水平渗透系数/垂直渗透系数
vka[0, :, :] = 1.05E-02
vka[1, :, :] = 1.05E-02
vka[2, :, :] = 5.90E-01
vka[3, :, :] = 5.90E-01
vka[4, :, :] = 5.90E-01
vka[5, :, :] = 6.51E-03
vka[6, :, :] = 6.51E-03
vka[7, :, :] = 1.53E-03
vka[8, :, :] = 1.53E-03
sy = 0.03*np.ones((nlay, nrow, ncol), dtype=np.float64)  # specific yield,给水度,无量纲
ss = 1e-5  # 单位储水量，单位：1/m，specific storage 贮水率
lpf = flopy.modflow.ModflowLpf(model=mf, hk=hk, vka=vka, sy=sy,
                               ss=ss, laytyp=laytyp, ipakcb=1, layvka=0)

# # 检查水平渗透系数输入是否正确
# plt.imshow(hk[0, :, :])
# plt.colorbar(shrink=0.5)
# plt.show()

# Basic Package (BAS),定义边界和初始水头
ibound = np.ones((nlay, nrow, ncol), dtype=np.int64)
ibound[0, :, 0] = -1  # 定水头边界ibound=-1
ibound[0, :, 49] = -1
strt = 3 * np.ones((nlay, nrow, ncol), dtype=np.float64)  # 定义初始水头值均为3
strt[0, :, 0] = 3.5
strt[0, :, 49] = 3.1
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)
# 无论是 ibound，strt，以及渗透系数等单元信息，均为 [z, x, y] 的三维数组形式，此处生成输出文件中的 *.bas 文件

# # # recharge 单位：m/d
# # rech = {0: 0.001, 1: 0.0015, 2: 0.0005}
# # rch = flopy.modflow.ModflowRch(mf, nrchop=3, rech=rech)
#
# 设置井（WEL）
# wel_spd = {0: [[0, 6, 4, 5]],
#            1: [[0, 6, 4, 0]],
#            }
# wel = flopy.modflow.ModflowWel(mf, stress_period_data=wel_spd)
#
# OC 非稳定流的输出每个应力期需单独设置
stress_period_data = {}
for kper in range(nper):
    for kstp in range(nstp[kper]):
        stress_period_data[(kper, kstp)] = ["save head", "save drawdown",
                                            "save budget", "print head", "print drawdown", "print budget"]
oc = flopy.modflow.ModflowOc(mf, stress_period_data=stress_period_data, compact=True)

# PCG 求解器
pcg = flopy.modflow.ModflowPcg(model=mf)


# # ---- 手动更改第三个应力期的 ibound ----
# def update_ibound_for_third_period():
#     global ibound
#     # 左右两侧设置为无通量边界
#     ibound[:, :, 0] = 0  # 左侧边界改为无通量
#     ibound[:, :, -1] = 0  # 右侧边界改为无通量
#     ibound[:, 0, :] = 0  # 顶部边界改为无通量
#     ibound[:, -1, :] = 0  # 底部边界改为无通量
#     # 更新 BAS 包中的 ibound
#     bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)
#     return bas
#
#
# # 在第三个应力期之前，调用该函数更新 ibound
# if dis.perlen[2]:
#     bas = update_ibound_for_third_period()

# LMT
lmt = flopy.modflow.ModflowLmt(mf, output_file_name='mt3d_link.ftl')
# write
mf.write_input()
# run
# success, mfoutput = mf.run_model(pause=False, report=True)
# if not success:
#     raise Exception('MODFLOW did not terminate normally.')

# 创建MT3DMS模型
mt = flopy.mt3d.Mt3dms(modelname='Jiading_test', version='mt3dms', exe_name='mt3dms5b',
                       modflowmodel=mf, model_ws='./mymodel')

# BTN 用于设置溶质运移的基本条件
icbund = np.ones((nlay, nrow, ncol))
sconc = np.zeros((nlay, nrow, ncol), dtype=np.float64)  # 初始浓度
# for i in range(nlay):
#     Sn = np.loadtxt(fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test\utchem\Sn_lay_{i+1}.txt')
#     sconc[i, :, :] = np.where(Sn != 0, 1000, 0)    # 二氯甲苯的溶解度(20℃)
prsity = 0.5
btn = flopy.mt3d.Mt3dBtn(mt, sconc=sconc, prsity=prsity, thkmin=0.01, tunit='D', munit='μg/L',
                         nprs=8, timprs=[730, 1460, 2190, 2920, 3650, 4380, 5110, 5840], icbund=icbund)
# 保存时间，每两年，2008，2010，2012，2014，2016，2018，2020，2022
# sconc初始浓度，prsity孔隙率，nprs保存次数，timprs表示在第几天保存，从零计

# ADV
adv = flopy.mt3d.Mt3dAdv(mt, mixelm=-1, percel=1)
# DSP
dsp = flopy.mt3d.Mt3dDsp(mt, al=27.93376743299898, dmcoef=0, trpt=0.1, trpv=0.01)
# al纵向弥散度，trpt横向弥散度与纵向弥散度之比，trpv垂直弥散度和纵向弥散度之比

# # SSM 源汇项
# 计算传质系数
alpha = 37.15
beta = 0.05**0.61
gamma = 1.24
D = 8.008825148097755e-07   # 扩散系数（分子扩散系数），单位为m2/s；6.5E-10~8.5E-10
L = 8.393231861364765        # 特征长度，单位为m；粘土或细粒介质，特征长度范围10E-6~10E-4之间；场地规模地下水模型的计算网格尺度，1~10m之间
# kc = 10E-6   # 传质系数，对于多孔介质中的对流传质，传质系数的范围可能会在10E-8~10E-6之间

C_solubility = 8090000  # Set the solubility concentration (C溶解度),单位μg/L
C_water = np.zeros((nlay, nrow, ncol))  # Initial water phase concentration, you may want to update this over time

# 初始化 flux 为一个空的字典，包含每个网格位置的通量列表
flux_data = {}

# Initialize the source-sink data dictionary for stress periods
ssm_data = {0: [], 1: [], 2: []}

# Iterate through each stress period to dynamically update water phase concentration
for per in range(nper):  # nper 是应力期数量
    for i in range(nlay):
        Sn = np.loadtxt(fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\Sn_lay_{i+1}.txt')
        Sn_nrow, Sn_ncol = Sn.shape  # 获取 Sn 的行数和列数

        # 确定当前应力期的时间步长
        current_perlen = perlen[per]  # 取当前应力期的长度
        current_nstp = nstp[per]  # 取当前应力期的时间步数
        dt = current_perlen / current_nstp  # 计算时间步长

        # 对于 S_n = 0 的区域，通过相邻网格的浓度差来进行扩散更新
        for row in range(min(nrow, Sn_nrow)):
            for col in range(min(ncol, Sn_ncol)):
                Sn_value = Sn[row, col]
                if Sn_value != 0:
                    current_flux = alpha * beta * (Sn_value ** gamma) * D / L * (C_solubility - C_water[i, row, col])
                    ssm_data[per].append((i, row, col, current_flux, 15))  # 源汇项
                    C_water[i, row, col] += current_flux * dt / (8 * 0.25 * (1 - Sn_value))
                else:
                    # 邻近网格的浓度差处理，注意边界条件
                    neighboring_concentration = 0
                    count = 0

                    # 检查上方是否在边界内
                    if row > 0:
                        neighboring_concentration += C_water[i, row - 1, col]
                        count += 1
                    # 检查下方是否在边界内
                    if row < nrow - 1:
                        neighboring_concentration += C_water[i, row + 1, col]
                        count += 1
                    # 检查左侧是否在边界内
                    if col > 0:
                        neighboring_concentration += C_water[i, row, col - 1]
                        count += 1
                    # 检查右侧是否在边界内
                    if col < ncol - 1:
                        neighboring_concentration += C_water[i, row, col + 1]
                        count += 1

                    # 如果有相邻网格，计算平均值
                    if count > 0:
                        neighboring_concentration /= count

                    # 通过邻近网格的浓度差进行扩散更新
                    diffusion_flux = 1e-6 * (neighboring_concentration - C_water[i, row, col])
                    C_water[i, row, col] += diffusion_flux * dt / (8 * 0.25)

# 初始化 SSM 包
ssm = flopy.mt3d.Mt3dSsm(mt, stress_period_data=ssm_data, mxss=5000)

# # GCG
# gcg = flopy.mt3d.Mt3dGcg(mt, mxiter=1, iter1=50, isolve=1, cclose=0.0001)
# mt.write_input()
# mt.run_model()

# MT3DMS 运行结果
conc = flopy.utils.UcnFile('./mymodel/MT3D001.UCN')
times = conc.get_times()
conc = conc.get_alldata()
conc = np.array(conc)
print(conc.shape)

# 行数向下为正
GW14 = conc[8, 4, 12, 34]
GW18 = conc[8, 4, 12, 16]
GW20 = conc[8, 4, 37, 15]
C = (GW14, GW18, GW20)
print(C)

# 平面单图输出
selected_time_step = 8  # 选择要查看的时间步，例如第5个时间步
selected_layer = 8  # 选择要查看的地层，例如第4层
# 对应指定timprs的平面浓度分布绘图并保存
fig1 = plt.figure(figsize=(6, 5))  # 设置单个图片的尺寸
# 去除四周边缘一圈数据
# trimmed_conc = conc[selected_time_step, selected_layer, 1:-1, 1:-1]  # 去掉最外面的一圈（行和列）
trimmed_conc = conc[selected_time_step, selected_layer]  # 不去掉最外面的一圈（行和列）
df = pd.DataFrame(trimmed_conc)  # 转换为DataFrame
df.to_csv(rf"H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\mymodel\Jiading_test_C_layer_{selected_layer+1}_time_{selected_time_step}.csv")
# 绘制指定时间步和地层的浓度分布
plt.imshow(trimmed_conc, cmap='Spectral_r')
plt.title(f'Concentration at Time Step {selected_time_step}, Layer {selected_layer + 1}')  # 标题显示时间步和地层
plt.colorbar(fraction=0.05, pad=0.05, shrink=0.5)
plt.show()

# # 剖面单图输出
# selected_time_step = 8  # 选择时间步，例如第 5 个时间步
# selected_row = 24  # 选择剖面列，例如第 25 列
#
# # 去除四周边缘一圈数据
# # trimmed_conc = conc[selected_time_step, :, selected_row, 1:-1]  # 去掉最外面一列，保持所有层
# trimmed_conc = conc[selected_time_step, :, selected_row]  # 不去掉最外面一列，保持所有层
# df = pd.DataFrame(trimmed_conc)  # 转换为DataFrame
# df.to_csv(rf"H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\mymodel\Jiading_test_C_XZ_time_{selected_time_step}_row_{selected_row+1}.csv")
#
# # 绘制剖面浓度分布
# plt.imshow(trimmed_conc, cmap='Spectral_r')
# plt.title(f'Concentration Profile at Time Step {selected_time_step}, Column {selected_row + 1}')
# plt.colorbar(fraction=0.05, pad=0.05, shrink=0.5)
# plt.show()
