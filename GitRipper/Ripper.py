import requests
import time
from random import choice
import pandas as pd

def get_item(d, keys):
    """
    Helper function to get a value from a nested dictionary
    The function returns None if the key is not found
    Args:
        d (dict)        : dictionary
        keys (list)     : list of keys to traverse the dictionary
    Returns:
        value of the key if found, None otherwise
    """
    for k in keys:
        if d is None:
            return None
        if k in d:
            d = d[k]
        else:
            return None
    return d

def get_repository_info(owner, repo, token) -> dict:
    """
    Get the repository info from for a given owner and repo
    Args:
        owner (str)     : owner of the repository
        repo (str)      : name of the repository
        token (str)     : github token
    Returns:
        data_dict (dict): dictionary containing the repository info
        rate_limit_info (dict): dictionary containing the rate limit info
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
    if response.status_code != 200:
        print(response.text)
        data_dict = {'owner':owner, 'repo':repo,'name': None, 'description': None, 'owner': None, 'licenseName': None,
                'licenseSpdxId': None, 'licenseUrl': None, 'shortDescriptionHTML': None,
                'repourl': None, 'createdAt': None, 'updatedAt': None, 'pushedAt': None,
                'forkCount': None, 'stargazerCount': None, 'issuesCount': None,
                'pullRequestsCount': None, 'readme': None}
        return None, None
    result = response.json()
    name = get_item(result, ['data','repository','name'])
    description = get_item(result,['data','repository','description'])
    shortDescriptionHTML = get_item(result,['data','repository','shortDescriptionHTML'])
    repourl = get_item(result,['data','repository','url'])
    createdAt = get_item(result,['data','repository','createdAt'])
    updatedAt = get_item(result,['data','repository','updatedAt'])
    pushedAt = get_item(result,['data','repository','pushedAt'])
    forkCount = get_item(result,['data','repository','forkCount'])
    stargazerCount = get_item(result,['data','repository','stargazerCount','totalCount'])
    issuesCount = get_item(result,['data','repository','issues','totalCount'])
    pullRequestsCount = get_item(result,['data','repository','pullRequests','totalCount'])
    readme = get_item(result,['data','repository','object','text'])
    owner = get_item(result,['data','repository','owner','login'])
    licenseName = get_item(result,['data','repository','licenseInfo','name'])
    licenseSpdxId = get_item(result,['data','repository','licenseInfo','spdxId'])
    licenseUrl = get_item(result,['data','repository','licenseInfo','url'])

    # get all rate limit info
    login = get_item(result,['data','viewer','login'])
    limit = get_item(result,['data','rateLimit','limit'])
    cost = get_item(result,['data','rateLimit','cost'])
    remaining = get_item(result,['data','rateLimit','remaining'])
    resetAt = get_item(result,['data','rateLimit','resetAt'])
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
    Get all commits information from a repository since a given date
    Args:
        owner (str)     : owner of the repository
        repo (str)      : name of the repository
        token (str)     : github token
        since (str)     : date in ISO 8601 format
    Returns:
        df_out (pd.DataFrame): dataframe containing the commits information
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
        if response.status_code != 200:
            print(response.text)
            return None
        result = response.json()
        history = get_item(result,['data','repository','defaultBranchRef','target','history'])
        hists = get_item(history, ['edges'])
        if hists is None:
            hists = []
        for edge in hists:
            node = get_item(edge,['node'])
            username = get_item(node,['author','user','login'])
            location = get_item(node,['author','user','location'])
            company = get_item(node,['author','user','company'])
            pronouns = get_item(node,['author','user','pronouns'])
            bio = get_item(node,['author','user','bio'])
            websiteUrl = get_item(node,['author','user','websiteUrl'])
            twitterUsername = get_item(node,['author','user','twitterUsername'])
            df_rows.append([get_item(node,['oid']), get_item(node,['messageHeadline']), 
                            get_item(node,['author','name']), 
                            get_item(node,['author','email']), username, location,
                           company, pronouns, bio, websiteUrl, twitterUsername, 
                           get_item(node, ['author','date']), get_item(node,['additions']), 
                           get_item(node, ['deletions'])])
        has_next_page = get_item(history,['pageInfo','hasNextPage'])
        cursor = get_item(history,['pageInfo','endCursor'])
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


def githubKeysInfo(token) -> dict:
    """
    Get the rate limit info from github api for a token
    Args:
        token (str)     : github token
    Returns:
        return_dict (dict): dictionary containing the rate limit info
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
            login = get_item(result,['data','viewer','login'])
            limit = get_item(result,['data','rateLimit','limit'])
            cost = get_item(result, ['data','rateLimit','cost'])
            remaining = get_item(result, ['data','rateLimit','remaining'])
            resetAt = get_item(result, ['data','rateLimit','resetAt'])
            return_dict = {'login': login, 'limit': limit,
                           'cost': cost, 'remaining': remaining, 'resetAt': resetAt}
            return return_dict
    else:
        print(f"Query failed with status code: {response.status_code}")
        return -1


class collect:
    def __init__(self, keys_list) -> None:
        """
        This function initializes the class with a list of keys
        If the key is valid, it adds the key to the keys_dict, otherwise it ignores it
        Args:
            keys_list (list): list of tuples containing the username and the API key
        Returns:
            None
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

    def refreshKeysHealth(self) -> None:
        """
        This function refreshes the health of all keys in the keys_dict
        Args:
            None
        Returns:
            None
        """
        for k in self.keys_dict.keys():
            self.keys_dict[k] = githubKeysInfo(k)

    def getBestKey(self) -> str:
        """
        This function returns the key with the highest remaining requests limit and waits for an hour if the limit is less than 10
        Args:
            None
        Returns:
            best_key (str): the key with the highest remaining requests limit
        """
        best_key = max(
            self.keys_dict, key=lambda k: self.keys_dict[k]['remaining'])
        if self.keys_dict[best_key]['remaining'] < 10:
            print(f"Waiting for an hour for key {best_key} to refresh")
            time.sleep(3600)
        best_key = max(
            self.keys_dict, key=lambda k: self.keys_dict[k]['remaining'])
        return best_key
    
    def getBestKeys(self, n) -> list:
        """
        This function returns the n keys with the highest remaining requests limit and greater than 10 remaining requests
        If the number of keys with remaining requests greater than 10 is less than n, the function duplicates the list of keys
        Args:
            n (int): number of keys to return
        Returns:
            keys_desc (list): list of keys with the highest remaining requests limit
        """
        keys_desc = sorted(self.keys_dict, key=lambda k: self.keys_dict[k]['remaining'], reverse=True)
        # select all keys with remaining requests greater than 10
        keys_desc = [k for k in keys_desc if self.keys_dict[k]['remaining'] > 10]
        if len(keys_desc) == 0:
            time.sleep(3600)
        if len(keys_desc) < n: #if length of keys_desc is less than n, duplicate the list to return n keys
            keys_desc = keys_desc * (n//len(keys_desc) + 1)
        return keys_desc[:n]
            

    def collectCommits(self, owner, repo, token=None, since="2007-01-01T00:00:00Z") -> pd.DataFrame:
        """
        This function collects all commits info from a repo since a given date and returns a pd.DataFrame object
        Args:
            owner (str)     : owner of the repo
            repo (str)      : name of the repo
            token (str)     : github token, if None, the function will select the token with the highest remaining requests limit
            since (str)     : date in ISO 8601 format, default is 2007-01-01T00:00:00Z
        Returns:
            df (pd.DataFrame): dataframe containing all commits info
        """
        if token is None:
            token = self.getBestKey()
        df = get_all_commits(owner, repo, token, since)
        self.refreshKeysHealth()
        return df

    def getRepoInfo(self, owner, repo, token=None) -> dict:
        """
        This function collects all commits from a repo since a given date and returns a pd.DataFrame object
        Args:
            owner (str)     : owner of the repo
            repo (str)      : name of the repo
            token (str)     : github token, if None, the function will select the token with the highest remaining requests limit
        Returns:
            d (dict): dictionary containing the repository info
        """
        if token is None:
            token = self.getBestKey()
        d, rl_dict = get_repository_info(owner, repo, token)
        self.keys_dict[token] = rl_dict
        return d
