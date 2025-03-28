from PE_Package.knowledge_base import Knowledges as Ks

tags = ['线性表', '定义', '顺序结构', '操作', '顺序表', '存储', '链表', '单链表', '双链表', '区别', '循环链表', '栈', '线性结构', '队列', '场景', '应用', '树', '树形结构', '二叉树', '遍历', '二叉搜索树', '效率', '哈希表', '集合结构', '图', '图型结构', '有向图', '无向图', '红黑树', '平衡', 'AVL树', '字典树', '实现', '构造', 'B树', '磁盘', '哈希冲突', '邻接表', '加权图', '最短路径', '算法', '有向无环图', '特点', '连通性', '稀疏矩阵', '矩阵', '压缩', '广义表', '递归', '链式', '串', '模式匹配', 'KMP算法', 'Boyer-Moore算法', '回溯算法', '优化', '分治法', '动态规划', '贪心算法', '哈夫曼编码', '哈夫曼树', '构建', '拓扑排序', '强连通分量', 'Tarjan算法', 'Kruskal算法', '最小生成树', 'Prim算法', 'Dijkstra算法', 'Floyd算法', 'Bellman-Ford算法', 'A*算法', '启发式搜索', '启发函数', '并查集', '集合', '数据结构', '路径压缩', '跳表', '索引', '维护', '线段树', '区间查询', '树状数组', '前缀和', '插入', '查找', '前缀匹配', '后缀数组', '字符串匹配', '后缀自动机', 'AC自动机', '多模式匹配', '分块算法', '字符串哈希', '哈希函数', '滚动哈希', '双哈希', '基数排序', '排序', '时间复杂度', '计数排序', '桶排序', '多路归并排序', '外部排序', '置换选择排序', 'B+树', '平衡树', '自平衡', '删除', '旋转', '二叉堆', '优先队列', '斐波那契堆', '左偏树', '伸展树', '自调整', '替罪羊树', '重构', '区间树', '持久化数据结构', '历史版本']

def ScreenLabels(user_input:str) -> list: #从输入的文本中直接字符串匹配，获得目标labels
    labels = []
    for tag in tags:
        if tag in user_input:
            labels.append(tag)
    return labels

def ScreenItem(labels:list) -> list: # 以目标labels筛选合适的
    res = []
    for item in Ks:
        for tag in item["label"]:
            if tag in labels:
                res.append(item)
    return res

def item2prompt(res:list) -> str: # 将搜索到的prompt组合
    prompt = "<Konwledge>\n"
    for item in res:
        prompt += "input:"+str(item["input"])+":\t"
        prompt += "output:"+str(item["output"])+"\n"
    prompt+= "\n</Knowledge>"
    return prompt

def AutoPromptRAG(user_input:str) -> str: # 封装上述操作
    labels = ScreenLabels(user_input)
    res = ScreenItem(labels)
    prompt = item2prompt(res)
    return prompt