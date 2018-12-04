import os
import thulac
# import jieba

def saveFile(path, content):
    fp = open(path, "w", encoding='utf8')
    fp.write(content)
    fp.close()
def readFile(path):
    fp = open(path, "r", encoding='utf8')
    content = fp.read()
    fp.close()
    return content

train_path = 'training/'
cut_path = 'cut/'

catelist = os.listdir(train_path)  # 获取该目录下所有子目录

thu1 = thulac.thulac(filt=True) # 初始化分词模型

for mydir in catelist:
    class_path = train_path + mydir + "/"  # 拼出分类子目录的路径
    cut_dir = cut_path + mydir + "/"  # 拼出分词后预料分类目录
    if not os.path.exists(cut_dir):  # 是否存在，不存在则创建
        os.makedirs(cut_dir)
    file_list = os.listdir(class_path)
    for file_path in file_list:
        fullname = class_path + file_path
        content = readFile(fullname).strip()  # 读取文件内容
        content = content.replace("\r\n", "").strip()  # 删除换行和多余的空格
        content_cut = thu1.cut(content)

        tmp_str = ''
        for word in content_cut:
            if 'n' in word[1]:
                tmp_str += word[0] + ' '
                saveFile(cut_dir + file_path, "".join(tmp_str))
        

print("分词结束")




# train_path = ''
# thu1 = thulac.thulac(filt=True)  #默认模式
# text = thu1.cut("我让北京爱天安门")  #进行一句话分词
# print(text)