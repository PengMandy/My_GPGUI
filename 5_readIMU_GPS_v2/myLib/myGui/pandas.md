# pandas 使用

## 讀檔案

```python
temp = pd.read_csv(path, sep=r'\s*,\s*', engine='python', skiprows=0)
```

## 得到data frame 檔案大小
```python
path = 'tt2.txt'
# 如果檔案裡有註解，則需加上comment引數，否則會錯
# 加入comment引數後pd在讀入數據會忽略引數部分，因此計算size時會比實際大小還要小
temp = pd.read_csv(path, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0)
N = len(temp.to_csv(index=False))
size = os.path.getsize(path)
print('N: ', N) # df 檔案大小
print('size: ', size) # 原始檔案大小
print(int(size / N))

```


