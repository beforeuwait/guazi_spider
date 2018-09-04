# 开发文档

    
|时间|撰写人|修订内容|备注|
|:-:|:---:|:-----:|:-:|
|2018-09-04|王家葳|建立文档|初稿|


> 目录

- 背景
- 总体设计
- 流程设计
- DB设计

## 背景

为“车价评估系统”做数据补充支撑

针对《瓜子二手车网》上已售车型的数据

制定并开发一款采集系统来完成

难点在于：

1. 需要登录
2. cookie有时效性
3. 单例脚本时间长

## 总体设计

![架构图][1]


## 流程设计

1. 由schedule启动任务
	
	- 向Task_Queue派发任务，启动一个节点为Session管理节点
	- 向Task_Queue派发任务，启动一个节点为Seed管理节点
	- 向Task_Queue派发任务，启动一个节点为Persistence管理节点 
   
2. SessionMangement节点
	
	- 实现登录，维护一个可采集的session列表
	- 删除失效session
	- 监听ssn_req队列，确认下次派发出session的数量

3. SeedMangement管理模块

	- 更新汽车品牌、车系
	- 生产种子列表
	- 向Task_Queue派发种子
	- 监听sed_req队列，确认下次派发出seed的数量

4. spider管理模块

	- 从Task_Queue队列里获取任务
	- 完成请求和解析
	- 向ps_queue放入待存储数据
	- 向sed_req队列反馈当前url的抓取状态
	- 向ssn_req队列反馈当前session的有效状态

5. Persistence管理模块
	
	- 从ps_queue队列获取待储存的数据
	- 完成数据存储

## DB设计

待编写
 

[1]: https://github.com/beforeuwait/guazi_spider/blob/master/%E7%93%9C%E5%AD%90%E6%8A%93%E5%8F%96%E7%B3%BB%E7%BB%9F%E6%9E%B6%E6%9E%84.jpg?raw=true 