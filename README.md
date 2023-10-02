
# GitRipper

GitRipper is a python module can be used to get repository and commits information given a public GitHub owner and repository. This module supports multiple API keys with built-in usage monitoring and balancing and can help with large-scale data collection.

### Installation/Importing
To import the module into your python code, clone the repository into your local drive. You can either choose to add `GitRipper` directory within the repo to python path. You can also import it by using `sys.path`

```python
import sys
sys.path.append("PATH_TO_GitRipper_Directory")
from GitRipper.Ripper import collect
```

### Usage

1. Initialize the object with keys list
```python
keys_list =  [
('User_1',  'Key_1'),
('User_2',  'Key_2'),
('User_3',  'Key_3')
]

collector =  collect(keys_list)
```
Here, `User_x` is the username of the owner of `Key_x`

2. Collect repository information given `owner` and `repository`
```python
dict_repo = collector.getRepoInfo(owner, repository)
```

This returns a dictionary in the following form

```python
data_dict = {
	'owner':owner,
	'repo':repo,
	'name': name,
	'description': description,
	'owner': owner,
	'licenseName': licenseName,
	'licenseSpdxId': licenseSpdxId,
	'licenseUrl': licenseUrl,
	'shortDescriptionHTML': shortDescriptionHTML,
	'repourl': repourl,
	'createdAt': createdAt,
	'updatedAt': updatedAt,
	'pushedAt': pushedAt,
	'forkCount': forkCount,
	'stargazerCount': stargazerCount,
	'issuesCount': issuesCount,
	'pullRequestsCount': pullRequestsCount,
	'readme': readme
}
```
3. Collect commits information given `owner` and `repository`

```python
df_commits = collector.collectCommits(owner, repository)
```
This returns a `pd.DataFrame` object containing the following columns

```python
columns =  ['Package',  'Slug',  'URL',  'oid','messageHeadline',  'author_name',  'author_email',  'author_user_login',  'author_user_location',  'author_user_company',  'author_user_pronouns',  'author_user_bio',  'author_user_websiteUrl',  'author_user_twitterUsername',  'author_date',  'additions',  'deletions']
```
The examples above illustrate the most basic usage for using `GitRipper`. Refer to the documentation below for additional methods 

## Documentation

### Class

#### `collect`

Initializes the class with a list of keys If the key is valid, it adds the key to the keys_dict, otherwise it ignores it

	Args:
		keys_list (list): list of tuples containing the username and the API key
	Returns:
		None

  

### Methods

#### `collector.refreshKeysHealth()`

This function refreshes the health of all keys in the keys_dict

	Args:
		None
	Returns:
		None

  

#### `collector.getBestKey()`

This function returns the key with the highest remaining requests limit and waits for an hour if the limit is less than 10

	Args:	
		None
	Returns:
		best_key (str): the key with the highest remaining requests limit

  

#### `collector.getBestKeys(n)`

This function returns the n keys with the highest remaining requests limit and greater than 10 remaining requests If the number of keys with remaining requests greater than 10 is less than n, the function duplicates the list of keys

	Args:
		n (int): number of keys to return
	Returns:
		keys_desc (list): list of keys with the highest remaining requests limit

#### `collector.getRepoInfo(self, owner, repo, token=None)`
This function collects all commits from a repo since a given date and returns a dictionary containing the repository information

	Args: 
		owner (str) : owner of the repo 
		repo (str) : name of the repo 
		token (str) : github token, if None, the function will select the token with the highest remaining requests limit 
	Returns: 
		d (dict): dictionary containing the repository info

#### `collector.collectCommits(owner, repo, token=None, since='2007-01-01T00:00:00Z')`

This function collects all commits info from a repo since a given date and returns a `pd.DataFrame` object

	Args:
		owner (str) : owner of the repo
		repo (str) : name of the repo
		token (str) : github token, if None, the function will select the token with the highest remaining requests limit
		since (str) : date in ISO 8601 format, default is 2007-01-01T00:00:00Z
	Returns:
		df (pd.DataFrame): dataframe containing all commits info

