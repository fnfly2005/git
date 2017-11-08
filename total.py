# -*-coding:utf-8-*-
import os as os
import pandas as pd
import numpy as np
import math

c_name = ["dt", "year", "month", "week", "weekdays", "source_type", "biz_unit", "end sea_type", "category_lvl1_name",
          "category_lvl2_name", "category_lvl3_name", "supplier_name", "brand_name", "topic_name", "topic_type_name",
          "province_name", "city_name","is_black","p_orders", "order_amt", "total_coupon"]

gmv = pd.read_csv('/home/xubinbin/total.txt', header=0, sep=',', quotechar='"', encoding='utf-8',
                  names=c_name)  # 文件路径里的“\”要改成“/”否则会提示unicodeescape' codec can't decode bytes in position 7-8: truncated \xXX escape

ntest = pd.DataFrame(columns=['pname', 'F', 'P_VALUE', 'Q95'])  # 创建一个空的数据框存放正态分布的F检验和95%的分位数
score = pd.DataFrame(columns=['dt', 'dif_score', 'p_name', 'p_name_1', 'p_name_2', 'p_name_3','dif_score_top3'])  # 创建一个空的数据框存放该维度集中值的历史数据
score_result = pd.DataFrame(columns=['dt', 'dif_score', 'p_name', 'p_name_1', 'p_name_2', 'p_name_3','dif_score_top3','dif_score_index'])  # 创建一个空的数据框存放该维度集中值的历史数据
for pname in ["source_type", "biz_unit", "end sea_type", "category_lvl1_name",
              "category_lvl2_name", "category_lvl3_name", "supplier_name", "brand_name", "topic_name",
              "topic_type_name", "province_name", "city_name","is_black"]:#列出所有要分析的维度
    p = pd.pivot_table(gmv, index=pname, values=["order_amt"], columns=["dt"], aggfunc=[np.sum],fill_value=0)  # 创建数据透视表
    p = p['sum']['order_amt'][:]  # 只保留“日期”一个列标签
    for i in range(0, p.columns.size):  # 遍历指标的所有历史数据
        try:
            p_sample = p.iloc[:, [i, i + 1]]  # iloc是按照序号切片，loc是按照标签名称切片
            p_sample['dif'] = abs(p_sample.iloc[:, 1] - p_sample.iloc[:, 0])  # 计算该维度每个水平的变化
            p_sample['dif_pct'] = p_sample['dif'] / p_sample['dif'].sum()  # 求各水平变化的占比
            top_size = int(math.ceil(p_sample.iloc[:,1][p_sample.iloc[:,1]>0].size * 0.2))
            p_dif = p_sample.sort(columns='dif', ascending=False).head(top_size)  # 总变化中排名前三的三个水平
            p_dif_score = p_dif['dif_pct'].sum()  # 该维度的集中值
            try:
                score = score.append(pd.DataFrame([[p.columns[i + 1], p_dif_score, pname, p_dif.index[0],
                                                    p_dif.index[1], p_dif.index[2], p_dif.iloc[0:2, 3].sum()]],
                                                  columns=['dt', 'dif_score', 'p_name', 'p_name_1', 'p_name_2',
                                                           'p_name_3', 'dif_score_top3']))
                # 将所有历史每天的维度名字，该维度集中值、该集中值对应的（前3个）水平名字等数据存放在事先建好的数据框中
            except IndexError:
                try:
                    score = score.append(pd.DataFrame(
                        [[p.columns[i + 1], p_dif_score, pname, p_dif.index[0], p_dif.index[1], '',
                          p_dif.iloc[0:1, 3].sum()]],
                        columns=['dt', 'dif_score', 'p_name', 'p_name_1', 'p_name_2', 'p_name_3', 'dif_score_top3']))
                except IndexError:
                    score = score.append(pd.DataFrame(
                        [[p.columns[i + 1], p_dif_score, pname, p_dif.index[0], '', '',
                          p_dif.iloc[0, 3].sum()]],
                        columns=['dt', 'dif_score', 'p_name', 'p_name_1', 'p_name_2', 'p_name_3', 'dif_score_top3']))
        except IndexError:  # 循环到最后i+1会变大到报index错误
            print "读取完毕"
    import scipy.stats as stats
    normal_test = stats.normaltest(score[score.iloc[:, 2] == pname].iloc[:, 1])  # 正态分布检验，给出F统计量以及P值，原假设是：属于正态分布
    from scipy.stats.mstats import mquantiles
    q95 = mquantiles(score[score.iloc[:, 2] == pname].iloc[:, 1], 0.95)  # 返回一个0.95分位数的数组：array([0.81680035])
    p_outlier = score[(score.iloc[:, 2] == pname) & (score.iloc[:, 1] > q95[0])]  # 判断历史上所有的异常值
    p_outlier['dif_score_index']=p_outlier.iloc[:,1]/q95[0]
    score_result = score_result.append(p_outlier)
    ntest = ntest.append(pd.DataFrame([[pname, normal_test[0], normal_test[1], q95[0]]],
                                      columns=['pname', 'F', 'P_VALUE', 'Q95']))
					  
score=score.sort(["dt","dif_score"],ascending=False)
score_result=score_result.sort(["dt","dif_score"],ascending=False)

ntest.to_csv('/home/xubinbin/ntest.csv',sep=',',header=True,index=False,mode='w',encoding='utf-8')
score.to_csv('/home/xubinbin/score.csv',sep=',',header=True,index=False,mode='w',encoding='utf-8')
score_result.to_csv('/home/xubinbin/score_result.csv',sep=',',header=True,index=False,mode='w',encoding='utf-8')
