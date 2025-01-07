import requests

def delete_all_mirrored_repos(gitea_username, gitea_token):
    headers = {
        'Authorization': f'token {gitea_token}',
        'Content-Type': 'application/json'
    }

    # 获取用户的所有仓库
    response = requests.get(f'http://git.tdengine.net:3000/api/v1/user/repos', headers=headers)
    repos = response.json()

    for repo in repos:
        # 检查是否为镜像仓库
        if repo.get('mirror', False) or repo.get('fork', False):
            print(f'Checking repository: {repo["full_name"]}')
            delete_response = requests.delete(f'http://git.tdengine.net:3000/api/v1/repos/{repo["full_name"]}', headers=headers)
            if delete_response.status_code == 204:
                print(f'Successfully deleted: {repo["full_name"]}')
            else:
                print(f'Failed to delete: {repo["full_name"]}, Status Code: {delete_response.status_code}, error: {delete_response.json()}')
# 用您的 Gitea 用户名和访问令牌调用函数
delete_all_mirrored_repos('root', '607733f7791d09258109a166b1e5f92550b57580')
