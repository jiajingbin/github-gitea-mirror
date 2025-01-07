#!/usr/bin/env python
# https://github.com/PyGithub/PyGithub
from helper import isBlacklistedRepository, isCustomRepository, log,getConfig,giteaCreateUserOrOrg,giteaSetRepoTopics,giteaSession,giteaCreateRepo,ghApi,giteaCreateOrg,giteaGetUser,config
from github import GithubException
from localCacheHelper import giteaExistsRepos,saveLocalCache
import time

def process_repository(repo, repo_map, gh, loop_count):
    real_repo = repo.full_name.split('/')[1]
    gitea_dest_user = repo.owner.login
    repo_owner = repo.owner.login

    log('Source Repository : {0}'.format(repo.full_name))

    if isBlacklistedRepository(repo.full_name):
        print("     ---> Warning : Repository Matches Blacklist")
        return loop_count

    if real_repo in repo_map:
        gitea_dest_user = repo_map[real_repo]

    gitea_uid = giteaGetUser(gitea_dest_user)

    if gitea_uid == 'failed':
        gitea_uid = giteaCreateUserOrOrg(gitea_dest_user, repo.owner.type)

    repo_name = "{0}".format(real_repo)

    m = {
        "repo_name": repo_name,
        "description": (repo.description or "not really known")[:255],
        "clone_addr": repo.clone_url,
        "mirror": True,
        "private": repo.private,
        "uid": gitea_uid,
    }

    status = giteaCreateRepo(m, repo.private, True)
    if status != 'failed':
        try:
            if status != 'exists':
                giteaExistsRepos['{0}/{1}'.format(repo.owner.login, repo_name)] = "{0}/{1}".format(gitea_dest_user, repo_name)
                topics = repo.get_topics()
                giteaSetRepoTopics(repo_owner, repo_name, topics)
        except GithubException as e:
            print("###[error] ---> Github API Error Occured !")
            print(e)
            print(" ")
    else:
        log(repo)

    if loop_count % 50 == 0:
        log(False)
        log('Time To Sleep For 5 Seconds')
        log(False)
        time.sleep(5)

    return loop_count

def repositorySource():
    config = getConfig()
    repo_map = config['repomap']
    gh = ghApi()
    loop_count = 0

    if "mirrorlist" in config:
        mirrorlist = config['mirrorlist']
        print(f"     ---> mirrorlist-{mirrorlist} Found in config.json and only repositories in the list will be mirrored")
        for repo in gh.get_user().get_repos():
            if isCustomRepository(repo.full_name) and not repo.fork:
                loop_count += 1
                loop_count = process_repository(repo, repo_map, gh, loop_count)
            else:
                continue
    else:
        print("     ---> Warning : No mirrorlist Found in config.json and all repositories will be mirrored")
        for repo in gh.get_user().get_repos():
            if not repo.fork:
                loop_count += 1
                loop_count = process_repository(repo, repo_map, gh, loop_count)
            else:
                continue

    saveLocalCache()
