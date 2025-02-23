#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 @Author: Jane
 @FileName: function_pyutchemflopy.py
 @DateTime: 2024/1/22 22:17
 @SoftWare: PyCharm
"""

import subprocess
import flopy
import re
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

config = {
    'font.family': 'Times New Roman',
    'font.size': 15,
    'font.serif': ['SimSun'],
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'mathtext.fontset': 'stix',
    'savefig.dpi': 300, }
plt.rcParams.update(config)


# 提取地层平面Sn的函数
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


def pyutchemflopy_model(file_path, P):
    # 将 file_path 写入到一个记录文件中,以便结果绘制时调用与模型一致的路径
    with open("path_record.txt", 'w') as record_file:
        record_file.write(file_path)

    por, Kx, Ky, a, Q, VOF, Srw, b, C0 = P
    """
    parameter interpretation
    por: 无量纲，土壤孔隙度
    Kx: mD,毫达西，x方向渗透率
    Ky: mD,毫达西，y方向渗透率
    a: 无量纲，Kz/Kx，z方向渗透率
    Q: m3/d，多相流中污染物泄露流量
    VOF: 无量纲，多相流中泄露污染物的体积分数
    Srw: 无量纲，液相残余饱和度，参考取值0.2
    b: 无量纲，Brooks-Corey 模型参数，参考取值2.0
    C0: mg/L，污染物饱和溶解度，用于定义溶质运移模型中污染物初始浓度
    """

    # 修改多相模型input，设置相关参数

    # 根据一个关键词，修改一个参数
    def one_keyword_modifying_one_parameter(file_path, keyword, new_data):
        """
        Replace the data in the next line after the specified keyword in a text file.

        Parameters:
        - file_path (str): The path to the input text file.
        - keyword (str): The keyword to search for.
        - new_data (str): The data to replace with.

        Returns:
        - str: The text with data replaced.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for i in range(len(lines)):
            if keyword in lines[i]:
                # Find the line with the keyword
                if i + 1 < len(lines):
                    # Check if there is a next line
                    lines[i + 1] = str(new_data) + '\n'

        with open(file_path, 'w') as file:
            file.writelines(lines)

    def two_keyword_modifying_multiple_parameters(file_path, first_keyword, second_keyword, Q, VOF):
        """
        Replace multiple parameters in the line after the second specified keyword in a text file.

        Parameters:
        - file_path (str): The path to the input text file.
        - first_keyword (str): The first keyword to search for.
        - second_keyword (str): The second keyword to search for.
        - Q (str): The value for the Q parameter.
        - VOF (str): The value for the VOF parameter.

        Returns:
        - str: The text with data replaced.
        """
        new_data_lines = [
            f"1      0      0      0      0      0      0      0",
            f"1      {str(Q)}      0      {str(VOF)}      0      0      0      0",
            f"1      0      0      0      0      0      0      0"
        ]

        with open(file_path, 'r') as file:
            lines = file.readlines()

        found_first_keyword = False

        for i in range(len(lines)):
            if first_keyword in lines[i]:
                found_first_keyword = True
            elif found_first_keyword and second_keyword in lines[i]:
                # Find the line after the second keyword
                if i + 1 < len(lines):
                    # Check if there are enough lines in new_data_lines
                    if i + len(new_data_lines) < len(lines):
                        # Replace multiple lines with new_data_lines
                        for j in range(len(new_data_lines)):
                            lines[i + j + 1] = new_data_lines[j] + '\n'
                    break

        with open(file_path, 'w') as file:
            file.writelines(lines)

    file_path = file_path

    # 设置孔隙度
    keyword1 = "*---- PORC1"
    new_data1 = P[0]
    one_keyword_modifying_one_parameter(file_path, keyword1, new_data1)

    # 设置X方向的K值，注意此处是渗透率，溶质运移模型中需转换为渗透系数
    keyword2 = "*---- PERMXC"
    new_data2 = P[1]
    one_keyword_modifying_one_parameter(file_path, keyword2, new_data2)

    # 设置Y方向的K值，注意此处是渗透率，溶质运移模型中需转换为渗透系数
    keyword3 = "*---- PERMYC"
    new_data3 = P[2]
    one_keyword_modifying_one_parameter(file_path, keyword3, new_data3)

    # 设置Z方向K值与X方向K值的比值
    keyword4 = "*---- CONSTANT PERMEABILITY MULTIPLIER FOR Z DIRECTION PERMEABILITY"
    new_data4 = P[3]
    one_keyword_modifying_one_parameter(file_path, keyword4, new_data4)

    # 设置源处的泄漏量和泄露浓度（体积分数）
    first_keyword = "CC  ID,INJ. RATE AND INJ. COMP. FOR RATE CONS. WELLS FOR EACH PHASE (L=1,3)"
    second_keyword = "*----  ID     QI(M,L)     C(M,KC,L)"
    Q_value = P[4]
    VOF_value = P[5]
    two_keyword_modifying_multiple_parameters(file_path, first_keyword, second_keyword, Q_value, VOF_value)

    # 第一部分：运行UTCHEM程序
    # 指定exe文件路径
    exe_path = r'G:\UTCHEM\utchem93.exe'

    # 指定输入文件路径(HEAD和INPUT文件)
    input_file_path = file_path
    # head 文件与input位于同一文件夹下
    head_file_path = os.path.join(os.path.dirname(file_path), "head")

    # 读取输入文件1(HEAD)的内容
    with open(head_file_path, 'r') as input_file1:
        input_content1 = input_file1.read()

    # 读取输入文件2(INPUT)的内容
    with open(input_file_path, 'r') as input_file2:
        input_content2 = input_file2.read()

    # 使用subprocess运行exe文件，并将两个输入文件的内容传递给它
    try:
        subprocess.run([exe_path], input=(input_content1 + input_content2).encode(), check=True)
        print(f'{exe_path} 运行成功！')
    except subprocess.CalledProcessError as e:
        print(f'运行 {exe_path} 时发生错误：{e}')

    # 第二部分：提取多相模型饱和度数据
    # extract the data of Sn in specific layer
    # i表示地层数，需要把所有地层都提取出来
    for i in [1, 2, 3]:
        filename = os.path.join(os.path.dirname(file_path), "UTEX01.SATP")
        # 关键词1：提取结果所在的时间
        main_keyword1 = 'TIME =       30.000000 DAYS'
        # 关键词2：提取对应相
        main_keyword2 = f'SAT. OF PHASE            2 IN LAYER            {i}'
        # 确定提取关键词1、2之后的数据行数
        num_lines = 210
        result = extract_data_layer(filename, main_keyword1, main_keyword2, num_lines)

        # Reshape the data into a 30×70 array   长70宽30
        heatmap_data = np.array(result[:2100]).reshape((30, 70))  # (NY,NX)

        # Save the heatmap data to a text file
        heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_lay_{i}.txt")
        np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')

    # 第三部分：耦合flopy
    modelname = "function_pyutchemflopy"  # 模型名称
    mf = flopy.modflow.Modflow(modelname, exe_name="mf2005", namefile_ext='nam', model_ws='./mymodel', version='mf2005')
    # 生成 mymodel 文件夹和 *.nam 文件

    # 网格信息及其离散化(DIS)
    Lx = 140.0  # x方向上长度
    Ly = 60.0  # y方向上长度
    nrow = 30  # 网格行数
    ncol = 70  # 网格列数
    delr = Lx / ncol  # x方向步长
    delc = Ly / nrow  # y方向步长

    nlay = 3  # 含水层数量
    ztop = 0 * np.ones((nrow, ncol), dtype=np.float32)  # 垂直方向12m，假设顶部高程0m
    zbotm = np.ones((nlay, nrow, ncol), dtype=np.float32)
    zbotm[0, :, :] = -4
    zbotm[1, :, :] = -8
    zbotm[2, :, :] = -12

    # 时间上划分(DIS)
    nper = 2  # 应力期个数
    steady = [True, False]  # 设置每个应力周期是否为稳定流，第一个应力期设置为稳定流，以创建初始水头便于后续模拟
    perlen = [30, 1000]  # 应力期长度，稳定流为任意值，非稳定流不同数值代表天数
    nstp = [30, 1000]  # 每个应力期的时间步数，本例100意为将一个应力期的100天划分为100次
    # step_interval_output = 2  # output will be saved every # of intervals
    dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr,
                                   delc=delc, top=ztop, botm=zbotm,
                                   nper=nper, perlen=perlen, nstp=nstp, steady=steady)
    # 生成了输出文件中的 *.dis 文件

    # 设置含水层特征(LPF)
    # 此处含水层由于DNAPLs自由相的存在，导致渗透系数发生变化，需根据DNAPLs饱和度分布进行换算，
    # 𝐾_𝑒𝑓𝑓=𝐾_𝑖*((1−𝑆_𝑁−𝑆_𝑟𝑤)/(1−𝑆_𝑟𝑤 ))^((2+3r_𝑏)/r_𝑏 )
    # 含水层类型,>0潜水含水层，=0承压含水层，<0可变
    laytyp = 1
    # 土壤固有渗透系数，单位𝑚/𝑑，，由多相模型的渗透率（Kx，Ky）转换得到，
    # 𝑲_𝒊=𝑘 𝛾/𝜇，流体比重𝛾=ρ𝑔，流体（水）动力黏质系数𝜇=1.01×10^(−3) 𝑝𝑎∙𝑠（20℃）
    Ki = 4.14
    # 液相残余饱和度，取经验值
    Srw = P[6]
    # Brooks-Corey 模型参数，取定值
    b = P[7]
    # 计算每一层对应的Keff
    hk = np.ones((nlay, nrow, ncol), dtype=np.float64)  # 水平渗透系数，单位：m/d
    for i in [1, 2, 3]:
        # 获取多相流模拟结果得到的对应地层NAPL饱和度分布
        Sn = np.loadtxt(f'Sn_J1_lay_{i}.txt')
        hk[i - 1, :, :] = Ki * ((1 - Sn - Srw) / (1 - Srw)) ** ((2 + 3 * b) / b)
        # 将受多相流影响后的渗透系数场保存至文本中
        hk_path = os.path.join(os.path.dirname(file_path), f"hk{i}.txt")
        np.savetxt(hk_path, hk[i - 1, :, :])
    # 垂直渗透系数，单位：m/d,当layvka≠0时，表示水平渗透系数/垂直渗透系数
    # 注意：此处是Kx/Kz，多相流模型中（new_data4）是Kz/Kx,即vka=1/a
    vka = 1 / a
    # specific yield,给水度,无量纲
    sy = np.ones((nlay, nrow, ncol), dtype=np.float64)
    sy[0, :, :] = 0.1
    sy[1, :, :] = 0.06
    sy[2, :, :] = 0.02
    # 单位储水量，单位：1/m，specific storage 贮水率
    ss = 1e-5
    lpf = flopy.modflow.ModflowLpf(model=mf, hk=hk, vka=vka, sy=sy,
                                   ss=ss, laytyp=laytyp, ipakcb=1, layvka=1)

    # # 检查水平渗透系数输入是否正确
    # plt.imshow(hk[0, :, :])
    # plt.colorbar(shrink=0.5)
    # plt.show()

    # Basic Package (BAS),定义边界和初始水头
    ibound = np.ones((nlay, nrow, ncol), dtype=np.int64)
    ibound[0, :, 0] = -1  # 定水头边界ibound=-1
    ibound[0, :, 69] = -1
    strt = 0 * np.ones((nlay, nrow, ncol), dtype=np.float64)  # 定义初始水头值均为0
    strt[0, :, 0] = 0
    strt[0, :, 69] = -2
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

    # LMT
    lmt = flopy.modflow.ModflowLmt(mf, output_file_name='mt3d_link.ftl')
    # write
    mf.write_input()
    # run
    success, mfoutput = mf.run_model(pause=False, report=True)
    if not success:
        raise Exception('MODFLOW did not terminate normally.')

    # 创建MT3DMS模型
    mt = flopy.mt3d.Mt3dms(modelname='function_pyutchemflopy', version='mt3dms', exe_name='mt3dms5b',
                           modflowmodel=mf, model_ws='./mymodel')

    # BTN 用于设置溶质运移的基本条件
    icbund = np.ones((nlay, nrow, ncol))
    # 初始浓度
    sconc = np.zeros((nlay, nrow, ncol), dtype=np.float64)
    # for i in [1, 2, 3]:
    #     # 根据NAPL相分布初步推测溶解度初始分布，存在NAPL的单元浓度基本维持在饱和值，其他地方假设无污染，浓度为0
    #     sconc = np.loadtxt(f'Sn_J1_lay_{i}.txt')
    #     sconc[sconc == 0] = 0
    #     sconc[sconc != 0] = 0
    btn = flopy.mt3d.Mt3dBtn(mt, sconc=sconc, prsity=0.25, thkmin=0.01, tunit='D', munit='mg/L',
                             nprs=4, timprs=[99, 399, 699, 999], icbund=icbund)
    # sconc初始浓度，prsity孔隙率，nprs保存次数，timprs表示在第30,60,90天保存

    # ADV
    adv = flopy.mt3d.Mt3dAdv(mt, mixelm=-1, percel=1)
    # DSP
    dsp = flopy.mt3d.Mt3dDsp(mt, al=30, dmcoef=0, trpt=0.1, trpv=0.01)
    # al纵向弥散度，trpt横向弥散度与纵向弥散度之比，trpv垂直弥散度和纵向弥散度之比

    # # SSM 源汇项
    # ssm_data = {0: [(0, 6, 4, 50, 2)], 1: [(0, 6, 4, 0, 2)]}   # 井的类型为2
    # ssm = flopy.mt3d.Mt3dSsm(mt, stress_period_data=ssm_data)
    ssm_data = {0: [], 1: []}
    # 设置1，2，3层污染源处的溶解浓度
    for i in [1, 2, 3]:
        sconc = np.loadtxt(f'Sn_J1_lay_{i}.txt')
        contaminated_cells = np.column_stack(np.where(sconc != 0))

        # Add source term for each contaminated cell in stress period 0
        for row, col in contaminated_cells:
            ssm_data[0].append((i, row, col, P[8], -1))

        # Add source term for each contaminated cell in stress period 1
        for row, col in contaminated_cells:
            ssm_data[1].append((i, row, col, P[8], -1))

    # Create Mt3dSsm object
    ssm = flopy.mt3d.Mt3dSsm(mt, stress_period_data=ssm_data)

    # GCG
    gcg = flopy.mt3d.Mt3dGcg(mt, mxiter=1, iter1=50, isolve=1, cclose=0.0001)
    mt.write_input()
    mt.run_model()

    return file_path


# file_path = "H:\\BaiduSyncdisk\\08researchprogress\\04Simulation\\pyGUI\\GUI_try1\\input"
# P = [0.3, 5000, 5000, 0.5, 8, 0.7, 0.2, 2.0, 1900]
# pyutchemflopy_model(file_path, P)
#
# # 下面是结果绘图部分，使用该部分须在上方file_path有输入的情况下才可，作为函数暂且无输入的话，用resultplot.py进行绘图
#
# # 绘制NAPL相饱和度平面X-Y分布
# # 提取指定地层的Sn数据
# def Sn_XY(lay):
#     filename = os.path.join(os.path.dirname(file_path), "UTEX01.SATP")
#     # 关键词1：提取结果所在的时间
#     main_keyword1 = 'TIME =       30.000000 DAYS'  # 提取的是模拟的最终结果30d
#     # 关键词2：提取对应相
#     main_keyword2 = f'SAT. OF PHASE            2 IN LAYER            {lay}'
#     # 确定提取关键词1、2之后的数据行数
#     num_lines = 210
#     result = extract_data_layer(filename, main_keyword1, main_keyword2, num_lines)
#
#     # Reshape the data into a 30×70 array   长70宽30
#     heatmap_data = np.array(result[:2100]).reshape((30, 70))  # (NY,NX)
#
#     # Save the heatmap data to a text file
#     heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_lay_{lay}.txt")
#     np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')
#
#     # 绘图显示平面X-YSn分布
#     plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
#     plt.colorbar(shrink=0.45)
#     plt.title(f'Sn of DNAPLs in lay{lay}')
#     plt.show()
#     print(f"Heatmap data saved to {heatmap_filename}")
#
#
# # # 运行Sn_XY(lay)
# # lay = 1  # 注意，此处的层是读取文件里关键词，不需要从0开始计
# # Sn_XY(lay)
#
# # 绘制NAPL相饱和度剖面X-Z分布
# # 基于PreProcess_Files2调取剖面数据，生成文件UTex01_XZ.MESH及UTex01_XZ.SATP
# # 指定exe文件路径
# exe_path1 = r'G:\UTCHEM\PreProcess_Files2.exe'
#
# # 指定输入文件路径(HEAD和INPUT文件)
# input_file_name = os.path.join(os.path.dirname(file_path), "UTex01.SATP")
# mesh_file_name = os.path.join(os.path.dirname(file_path), "UTex01.MESH")
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
#
#
# # 此时得到UTex01_XZ.SATP，即NAPL相剖面分布情况，从该文件中调取对应位置剖面数据并绘图
# def Sn_XZ(row):
#     filename = os.path.join(os.path.dirname(file_path), "UTex01_XZ.SATP")
#     # 关键词1：提取结果所在的时间
#     main_keyword1 = 'TIME =       30.000000 DAYS'
#     # 关键词2：提取对应相
#     main_keyword2 = f'SAT. OF PHASE	2 	IN LAYER            {row}'
#     # 确定提取关键词1、2之后的数据行数
#     num_lines = 3
#     result = extract_data_row(filename, main_keyword1, main_keyword2, num_lines)
#     num = len(result)
#     # print(num)
#     # print(result)
#     # Reshape the data
#     heatmap_data = np.array(result[:210]).reshape((3, 70))  # (NZ,NX)
#
#     # Save the heatmap data to a text file
#     heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_row_{row}.txt")
#     np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')
#
#     # 绘图显示剖面X-ZSn分布
#     plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
#     plt.colorbar(shrink=0.45)
#     plt.title(f'Sn of DNAPLs in row {row}')
#     plt.show()
#     print(f"Heatmap data saved to {heatmap_filename}")
#
#
# # # 运行Sn_XZ(row)
# # row = 16  # 注意，此处的层是读取文件里关键词，不需要从0开始计
# # Sn_XZ(row)
#
# # 绘制NAPL相饱和度剖面Y-Z分布
# # 基于PreProcess_Files2调取剖面数据，生成文件UTex01_XZ.MESH及UTex01_XZ.SATP
# # 指定exe文件路径
# exe_path2 = r'G:\UTCHEM\PreProcess_Files2.exe'
#
# # 指定输入文件路径(HEAD和INPUT文件)
# input_file_name = os.path.join(os.path.dirname(file_path), "UTex01.SATP")
# mesh_file_name = os.path.join(os.path.dirname(file_path), "UTex01.MESH")
#
# # 指定剖面参数X-Z or Y-Z
# parameter = 'Y-Z'
#
# # 构建命令行参数列表
# command = [exe_path2, input_file_name, mesh_file_name, parameter]
#
# # 使用subprocess运行exe文件，并将命令行参数传递给它
# try:
#     subprocess.run(command, check=True)
#     print(f'{exe_path2} 运行成功！')
# except subprocess.CalledProcessError as e:
#     print(f'运行 {exe_path2} 时发生错误：{e}')
#
#
# # 此时得到UTex01_YZ.SATP，即NAPL相剖面分布情况，从该文件中调取对应位置剖面数据并绘图
# def Sn_YZ(col):
#     filename = os.path.join(os.path.dirname(file_path), "UTex01_YZ.SATP")
#     # 关键词1：提取结果所在的时间
#     main_keyword1 = 'TIME =       30.000000 DAYS'
#     # 关键词2：提取对应相
#     main_keyword2 = f'SAT. OF PHASE	2 	IN LAYER            {col}'
#     # 确定提取关键词1、2之后的数据行数
#     num_lines = 3
#     result = extract_data_row(filename, main_keyword1, main_keyword2, num_lines)
#     num = len(result)
#     # print(num)
#     # print(result)
#     # Reshape the data into a 10×30 array   长30宽10
#     heatmap_data = np.array(result[:90]).reshape((3, 30))  # (NZ,NY)
#
#     # Save the heatmap data to a text file
#     heatmap_filename = os.path.join(os.path.dirname(file_path), f"Sn_J1_col_{col}.txt")
#     np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')
#
#     # 绘图显示剖面Y-ZSn分布
#     plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
#     plt.colorbar(shrink=0.45)
#     plt.title(f'Sn of DNAPLs in col {col}')
#     plt.show()
#     print(f"Heatmap data saved to {heatmap_filename}")
#
#
# # # 运行Sn_YZ(col)
# # col = 10  # 注意，此处的层是读取文件里关键词，不需要从0开始计
# # Sn_YZ(col)
#
#
# # 水头结果绘图
# def head_plot(global_file_path):
#     # 获取数据
#     hds_file_path = os.path.join(os.path.dirname(global_file_path), "mymodel", "function_pyutchemflopy.hds")
#     headobj = flopy.utils.binaryfile.HeadFile(hds_file_path)
#     head = headobj.get_data()[2]  # 0：初始时刻水头，1，2对应应力期
#     # 将水头数据保存至表格中
#     df = pd.DataFrame(head)
#     # df.to_csv(r".\mymodel\function_pyutchemflopy_H%s.csv" % i)  # i不影响水头结果
#     df.to_csv(r".\mymodel\function_pyutchemflopy_H.csv")
#
#     # 水头分布图
#     fig = plt.figure(figsize=(12, 8))
#     ax1 = fig.add_subplot(1, 2, 1)
#     head_p = ax1.imshow(head)
#     plt.title('Head (m)')
#     plt.colorbar(head_p, fraction=0.05, pad=0.05, shrink=0.3)
#     plt.show()
#
#
# # # 运行head_plot
# # head_plot(global_file_path)
#
# # 污染浓度结果绘图
# conc = flopy.utils.UcnFile('./mymodel/MT3D001.UCN')
# times = conc.get_times()
# conc = conc.get_alldata()
# conc = np.array(conc)
#
#
# # print(conc.shape)
#
#
# # 对应最终timprs的平面X-Y浓度分布绘图
# def concentration_XY(lay, conc):
#     fig = plt.figure(figsize=(15, 60))
#     num_timprs = 3  # timprs最大时，绘制模拟最终结果的图
#
#     df = pd.DataFrame(conc[num_timprs, lay])
#     output_folder = os.path.join(".", "mymodel")
#     os.makedirs(output_folder, exist_ok=True)
#     csv_file_path = os.path.join(output_folder, f"function_pyutchemflopy_C_layer{lay}.csv")
#     df.to_csv(csv_file_path, index=False)
#
#     ax = fig.add_subplot(1, 1, 1)
#     ax.imshow(conc[num_timprs, lay], cmap='Spectral_r')
#     plt.show()
#
#
# # # 运行concentration_XY
# # lay = 0
# # concentration_XY(lay, conc)
#
#
# # 对应最终timprs的剖面X-Z浓度分布绘图
# def concentration_XZ(row, conc):
#     fig = plt.figure(figsize=(15, 60))
#     num_timprs = 3  # timprs最大时，绘制模拟最终结果的图
#
#     df = pd.DataFrame(conc[num_timprs, :, row, :])  # [timprs, nlay, nrow, ncol ]
#     output_folder = os.path.join(".", "mymodel")
#     os.makedirs(output_folder, exist_ok=True)
#     csv_file_path = os.path.join(output_folder, f"function_pyutchemflopy_C_layer{row}.csv")
#     df.to_csv(csv_file_path, index=False)
#
#     ax = fig.add_subplot(1, 1, 1)
#     ax.imshow(conc[num_timprs, :, row], cmap='Spectral_r')  # 注意对于X-Z，conc[num_timprs, :, row]
#     plt.show()
#
#
# # # 运行concentration_XZ
# # row = 15
# # concentration_XZ(row, conc)
#
#
# # 对应最终timprs的剖面Y-Z浓度分布绘图
# def concentration_YZ(col, conc):
#     fig = plt.figure(figsize=(15, 60))
#     num_timprs = 3  # timprs最大时，绘制模拟最终结果的图
#
#     df = pd.DataFrame(conc[num_timprs, :, :, col])  # [timprs, nlay, nrow, ncol ]
#     output_folder = os.path.join(".", "mymodel")
#     os.makedirs(output_folder, exist_ok=True)
#     csv_file_path = os.path.join(output_folder, f"function_pyutchemflopy_C_layer{col}.csv")
#     df.to_csv(csv_file_path, index=False)
#
#     ax = fig.add_subplot(1, 1, 1)
#     ax.imshow(conc[num_timprs, :, :, col], cmap='Spectral_r')  # 注意对于X-Z，conc[num_timprs, :, :, col]
#     plt.show()
#
#
# # # 运行concentration_YZ
# # col = 15
# # concentration_YZ(col, conc)
