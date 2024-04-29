import requests
import json

# 华为云API配置
IAM_AccountName = ""
IAM_UserName = ""
IAM_Password = ""
IAM_Project_ID = "ap-southeast-3"

# 华为云DNS配置
HUAWEI_DNS_ZONE_ID = ""
HUAWEI_DNS_TTL = 300
HUAWEI_DNS_DOMAIN_NAME_V4 = ""
HUAWEI_DNS_DOMAIN_NAME_V6 = ""

# Nezha API配置
Nezha_Server_ID = 93
Nezha_API_Endpoint_URL = "https://XXX.com/api/v1/server/details"
Nezha_API_Token = ""


# 主函数
def main():
    ipv4, ipv6 = get_server_addresses()
    if ipv4 or ipv6:
        update_dns_records(ipv4, ipv6)
    else:
        print("No server addresses retrieved.")

def handler(event, context):
    main()

if __name__ == "__main__":
    main()





# 获取华为云身份验证的Token
def get_XSubjectToken():
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "domain": {"name": IAM_AccountName},
                        "name": IAM_UserName,
                        "password": IAM_Password
                    }
                }
            },
            "scope": {
                "project": {
                    "name": IAM_Project_ID
                }
            }
        }
    }

    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.headers.get('X-Subject-Token')

# 获取 status.blueskyxn.com 的 IPv4 和 IPv6 地址
def get_server_addresses():
    headers = {
        'Authorization': f'{Nezha_API_Token}'
    }
    params = {
        'id': Nezha_Server_ID  # 服务器 ID
    }
    response = requests.get(Nezha_API_Endpoint_URL, headers=headers, params=params)
    data = response.json()
    if data['code'] == 0 and data['result']:
        ipv4 = data['result'][0]['ipv4'].split(',')[0] if data['result'][0]['ipv4'] else ""
        ipv6 = data['result'][0]['ipv6'].split(',')[0] if data['result'][0]['ipv6'] else ""
        return ipv4, ipv6
    return None, None

# 创建单个DNS记录
def create_dns_record(zone_id, XSTOKEN, domain_name, record_values, record_type, ttl=HUAWEI_DNS_TTL):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    data = {
        "name": domain_name + ".",
        "type": record_type,
        "ttl": ttl,
        "records": record_values
    }
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": XSTOKEN
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 202:
        print(f"Record {record_type} created successfully for {domain_name}: {response.json()}")
    else:
        print(f"Failed to create record {record_type} for {domain_name}: {response.status_code}, {response.text}")
    # 判断是否需要删除多余的记录
    cleanup_dns_records(zone_id, XSTOKEN, domain_name, record_type)

# 查询DNS记录集
def query_record_sets(zone_id, XSTOKEN, domain_name, record_type):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    params = {"type": record_type, "name": domain_name + '.'}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['recordsets']
    else:
        print(f"Failed to query records for {domain_name}: {response.status_code}")
        return []

# 删除多余的DNS记录
def cleanup_dns_records(zone_id, XSTOKEN, domain_name, record_type):
    existing_records = query_record_sets(zone_id, XSTOKEN, domain_name, record_type)
    if len(existing_records) > 1:
        sorted_records = sorted(existing_records, key=lambda x: x['updated_at'], reverse=True)
        records_to_delete = sorted_records[1:]  # 保留最新的记录，删除其他记录
        for record in records_to_delete:
            delete_dns_record(zone_id, XSTOKEN, record['id'])

# 删除单个DNS记录
def delete_dns_record(zone_id, XSTOKEN, record_id):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets/{record_id}"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    response = requests.delete(url, headers=headers)
    if response.status_code in [200, 202, 204]:
        print(f"Successfully deleted record ID: {record_id}")
    else:
        print(f"Failed to delete record ID: {record_id}: {response.status_code}, {response.text}")

# 更新 DNS 记录
def update_dns_records(ipv4, ipv6):
    XSTOKEN = get_XSubjectToken()
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    # 更新 IPv4 记录
    if ipv4:
        create_dns_record(HUAWEI_DNS_ZONE_ID, XSTOKEN, HUAWEI_DNS_DOMAIN_NAME_V4, [ipv4], "A")
    # 更新 IPv6 记录
    if ipv6:
        create_dns_record(HUAWEI_DNS_ZONE_ID, XSTOKEN, HUAWEI_DNS_DOMAIN_NAME_V6, [ipv6], "AAAA")

