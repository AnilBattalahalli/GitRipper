import requests
import time
from random import choice
import pandas as pd


def get_repository_info(owner, repo, token) -> dict:
    """
    Get the repository info from github api
    """
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': f'Bearer {token}'}

    query = """
    query {
      repository(owner: "%s", name: "%s") {
        name
        description
        shortDescriptionHTML
        url
        createdAt
        updatedAt
        pushedAt
        forkCount
        stargazerCount: stargazers {
          totalCount
        }
        issues(states: OPEN) {
          totalCount
        }
        pullRequests(states: OPEN) {
          totalCount
        }
        owner {
          login
        }
        licenseInfo {
            name
            spdxId
            url
            }
        object(expression: "HEAD:README.md") {
          ... on Blob {
            text
          }
        }
      }
      viewer {
            login
            }
      rateLimit {
        limit
        cost
        remaining
        resetAt
      }
    }
    """ % (owner, repo)

    response = requests.post(url, json={'query': query}, headers=headers)
    result = response.json()
    name = result['data']['repository']['name']
    description = result['data']['repository']['description']
    shortDescriptionHTML = result['data']['repository']['shortDescriptionHTML']
    repourl = result['data']['repository']['url']
    createdAt = result['data']['repository']['createdAt']
    updatedAt = result['data']['repository']['updatedAt']
    pushedAt = result['data']['repository']['pushedAt']
    forkCount = result['data']['repository']['forkCount']
    stargazerCount = result['data']['repository']['stargazerCount']['totalCount']
    issuesCount = result['data']['repository']['issues']['totalCount']
    pullRequestsCount = result['data']['repository']['pullRequests']['totalCount']
    readme = result['data']['repository']['object']['text']
    owner = result['data']['repository']['owner']['login']
    licenseName = result['data']['repository']['licenseInfo']['name']
    licenseSpdxId = result['data']['repository']['licenseInfo']['spdxId']
    licenseUrl = result['data']['repository']['licenseInfo']['url']

    # get all rate limit info
    login = result['data']['viewer']['login']
    limit = result['data']['rateLimit']['limit']
    cost = result['data']['rateLimit']['cost']
    remaining = result['data']['rateLimit']['remaining']
    resetAt = result['data']['rateLimit']['resetAt']
    rate_limit_info = {'login': login, 'limit': limit, 'cost': cost,
                       'remaining': remaining, 'resetAt': resetAt}

    data_dict = {'owner':owner, 'repo':repo,'name': name, 'description': description, 'owner': owner, 'licenseName': licenseName, 
                'licenseSpdxId': licenseSpdxId, 'licenseUrl': licenseUrl, 'shortDescriptionHTML': shortDescriptionHTML,
                'repourl': repourl, 'createdAt': createdAt, 'updatedAt': updatedAt, 'pushedAt': pushedAt,
                'forkCount': forkCount, 'stargazerCount': stargazerCount, 'issuesCount': issuesCount,
                'pullRequestsCount': pullRequestsCount, 'readme': readme}

    return data_dict, rate_limit_info


def get_all_commits(owner, repo, token, since) -> pd.DataFrame:
    """
    Get all commits from a repository since a given date
    """
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': f'Bearer {token}'}
    query = """
    query($cursor: String) {
        repository(owner: "%s", name: "%s") {
            defaultBranchRef {
                target {
                    ... on Commit {
                    history(first: 100, after: $cursor,  since: "%s") {
                        pageInfo {
                        hasNextPage
                        endCursor
                        }
                        edges {
                        node {
                            oid
                            messageHeadline
                            author {
                            name
                            email
                            date
                            user {
                                login
                                location
                                company
                                pronouns
                                bio
                                websiteUrl
                                twitterUsername
                            }
                            }
                            additions
                            deletions
                        }
                        }
                    }
                    }
                }
            }
        }
    }
    """ % (owner, repo, since)
    # print(query)
    df_rows = []
    has_next_page = True
    cursor = None
    while has_next_page:
        variables = {'cursor': cursor}
        response = requests.post(
            url, json={'query': query, 'variables': variables}, headers=headers)
        result = response.json()
        history = result['data']['repository']['defaultBranchRef']['target']['history']
        for edge in history['edges']:
            node = edge['node']
            if node['author']['user'] is None:
                username = None
                location = None
                company = None
                pronouns = None
                bio = None
                websiteUrl = None
                twitterUsername = None
            else:
                username = node['author']['user']['login']
                location = node['author']['user']['location']
                company = node['author']['user']['company']
                pronouns = node['author']['user']['pronouns']
                bio = node['author']['user']['bio']
                websiteUrl = node['author']['user']['websiteUrl']
                twitterUsername = node['author']['user']['twitterUsername']
            df_rows.append((node['oid'], node['messageHeadline'], node['author']['name'], node['author']['email'], username, location,
                           company, pronouns, bio, websiteUrl, twitterUsername, node['author']['date'], node['additions'], node['deletions']))
        has_next_page = history['pageInfo']['hasNextPage']
        cursor = history['pageInfo']['endCursor']
    df_out = pd.DataFrame(df_rows, columns=['oid', 'messageHeadline', 'author_name', 'author_email', 'author_user_login', 'author_user_location', 'author_user_company',
                          'author_user_pronouns', 'author_user_bio', 'author_user_websiteUrl', 'author_user_twitterUsername', 'author_date', 'additions', 'deletions'])
    # add repo name and owner to the dataframe
    df_out['repo_name'] = repo
    df_out['repo_owner'] = owner
    #Put owner and repo name in the first two columns
    cols = df_out.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    df_out = df_out[cols]
    return df_out


def githubKeysInfo(token):
    """
    Get the rate limit info from github api for a token
    """
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': f'Bearer {token}'}

    query = """
        query {
            viewer {
            login
            }
            rateLimit {
            limit
            cost
            remaining
            resetAt
            }
        }
  """

    response = requests.post(url, json={'query': query}, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print(f"Error: {result['errors'][0]['message']}")
            return -1
        else:
            login = result['data']['viewer']['login']
            limit = result['data']['rateLimit']['limit']
            cost = result['data']['rateLimit']['cost']
            remaining = result['data']['rateLimit']['remaining']
            resetAt = result['data']['rateLimit']['resetAt']
            return_dict = {'login': login, 'limit': limit,
                           'cost': cost, 'remaining': remaining, 'resetAt': resetAt}
            return return_dict
    else:
        print(f"Query failed with status code: {response.status_code}")
        return -1


class collect:
    def __init__(self, keys_list) -> None:
        """
        keys_list: list of tuples (username, key)
        """
        d = dict()
        for k in keys_list:
            r = githubKeysInfo(k[1])
            if r == -1:
                print(f"Key {k[0]} failed")
            else:
                d[k[1]] = r
        self.keys_dict = d
        self.keys_list = list(self.keys_dict.keys())

    def refreshKeysHealth(self):
        """
        This function refreshes the health of all keys in the keys_dict
        """
        for k in self.keys_dict.keys():
            self.keys_dict[k] = githubKeysInfo(k)

    def getBestKey(self):
        """
        This function returns the key with the highest remaining requests limit and waits for an hour if the limit is less than 10
        """
        best_key = max(
            self.keys_dict, key=lambda k: self.keys_dict[k]['remaining'])
        if self.keys_dict[best_key]['remaining'] < 10:
            print(f"Waiting for an hour for key {best_key} to refresh")
            time.sleep(3600)
        best_key = max(
            self.keys_dict, key=lambda k: self.keys_dict[k]['remaining'])
        return best_key
    
    def getBestKeys(self, n):
        """
        This function returns the n keys with the highest remaining requests limit and greater than 10 remaining requests
        """
        keys_desc = sorted(self.keys_dict, key=lambda k: self.keys_dict[k]['remaining'], reverse=True)
        # select all keys with remaining requests greater than 10
        keys_desc = [k for k in keys_desc if self.keys_dict[k]['remaining'] > 10]
        if len(keys_desc) < n: #if length of keys_desc is less than n, duplicate the list to return n keys
            keys_desc = keys_desc * (n//len(keys_desc) + 1)
        return keys_desc[:n]
            

    def collectCommits(self, owner, repo, token=None, since="2007-01-01T00:00:00Z"):
        """
        This function collects all commits from a repo since a given date and returns a dataframe
        owner: owner of the repo
        repo: name of the repo
        since: date in ISO 8601 format
        """
        if token is None:
            token = self.getBestKey()
        df = get_all_commits(owner, repo, token, since)
        self.refreshKeysHealth()
        return df

    def getRepoInfo(self, owner, repo, token=None):
        """
        This function collects all commits from a repo since a given date and returns a dataframe
        owner: owner of the repo
        repo: name of the repo
        """
        if token is None:
            token = self.getBestKey()
        d, rl_dict = get_repository_info(owner, repo, token)
        self.keys_dict[token] = rl_dict
        return d
