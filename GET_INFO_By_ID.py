import requests

# 设置 API 端点
url = 'https://XXX.com/api/v1/server/details'
# 替换以下 Token
token = ''
#设置服务器查询参数
serverid = 93
# 设置请求头部，包含认证 Token
headers = {
    'Authorization': f'{token}'
}

# 设置查询参数
params = {
    'id': serverid  # 服务器 ID
}

# 发送 GET 请求
response = requests.get(url, headers=headers, params=params)

# 获取响应数据
data = response.json()

# 提取服务器信息
if data['code'] == 0 and data['result']:
    server_info = data['result'][0]  # 提取第一个服务器的信息
    ipv4 = server_info['ipv4'].split(',')[0] if server_info['ipv4'] else ""
    ipv6 = server_info['ipv6'].split(',')[0] if server_info['ipv6'] else ""

    print("IPv4:", ipv4)
    print("IPv6:", ipv6)
else:
    print("没有找到服务器信息或返回错误")

# 打印完整的响应数据（可选）
# print(data)
