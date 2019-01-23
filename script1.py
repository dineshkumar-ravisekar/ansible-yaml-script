# Before run this Script you need to check
# the below imported packages were installed or not
 
from github import Github
from jira import JIRA
import requests
from requests.auth import HTTPBasicAuth
import json
from base64 import b64encode, b64decode
 
def createNewBranch(oldBranch, newBranch):
 
    user = login.get_user('Arunvenkat0') # replace the user name
    repo = user.get_repo('Test') # replace the repository name
    branch = repo.get_branch(oldBranch)
    repo.create_git_ref(ref='refs/heads/' + newBranch, sha=branch.commit.sha)
    print("New branch {} had been created successfully".format(newBranch))
 
def testMerge(base, branches):
 
    for branch in branches:
        print(" Created pull request for branches {0} <-- {1}".format(base, branch))
        print(" Branches were merged {0} <-- {1}".format(base, branch))
 
 
def merge_branches(base, branches):
 
    login = Github('arun.venkat', 'Password') # add the credential which is having access to create pull request and merge it.
 
    print(" Logged in the Github account")
    user = login.get_user('Arunvenkat0') # replace the user name
    repo = user.get_repo('Test') # replace the repository name
    for branch in branches:
        try:
            pullRequest = repo.create_pull('Pull request from Python', 'Description for the pull request', base, branch)  # Create pullRequest
            commits= [commit for commit in pullRequest.get_commits()]  # Get all the commits in feature branch
            print(" CommitId's for {0}\n{1}".format(branch, commits))  # Print the commit id's
            pullMerge = pullRequest.merge('merge the pullRequest from Pyhton', 'description for the merge', 'merge')  # Merge created pullRequest
            print(" Branches were merged {0} <-- {1}".format(base, branch))
        except:
            print(" The {0} and {1} branches wasn't merged. Please check the Github repo in WEB".format(base, branch))
            print(" The error might be: \n {0} \n {1}".format(pullRequest, pullMerge))  # Print the error messages if throws any errors during the pullRequest or Merge
 
def fetch_branches(mergeBranch, jira):
    
    restURL = "https://usesi1.atlassian.net/rest/api/2/project/MAG/version?status=unreleased&orderBy=name"  # Get all unreleased versions for the Projects(Magento Features)
    print("Reading current release version...")
 
    response = requests.get(restURL, auth=HTTPBasicAuth(jiraUname, jiraPassw))
    try:
 
        versionId = response.json()['values'][0]['id']
    except:
        print("The project {} doesn't have any release versions".format(projectKey))
 
        return 
    #versionName = response.json()['values'][0]['name']
    #versionName = "release/rc-"+versionName
    #print("Current release versionID is {}".format(versionName))
    
    restURL = "http://usesi1.atlassian.net/rest/api/latest/search?jql=Project=MAG%20AND%20fixVersion='{}'&startAt=0&maxResult=1000".format(versionId)  # Get all the issues from the version
    print("Reading release-note version {}".format(versionId))
    response = requests.get(restURL, auth=HTTPBasicAuth(jiraUname, jiraPassw))
    issues = response.json()['issues']
    if issues:
        print("Fetching all issues in the release versionID {}".format(versionId))
    else:
        print(" There is no issues found in this release versionID {}".format(versionId))
        return
    for issue in issues:
        issueObject = jira.issue(issue['id'])
        if str(issueObject.fields.status) == "Ready For Deployment":
            restURL = "https://usesi1.atlassian.net/rest/dev-status/latest/issue/detail?issueId={}&applicationType=github&dataType=pullrequest".format(issue['id'])  # Get branch names in the issues.
            response = requests.get(restURL, auth=HTTPBasicAuth(jiraUname, jiraPassw))
            jsonData = response.json()
            print("\nReading branch names from the issue {0}\n There is {1} branch(es) in the issue".format(issue['key'], len(jsonData['detail'][0]['branches'])))
            branch=[]
            for i in range(len(jsonData['detail'][0]['pullRequests'])):
                print(jsonData['detail'][0]['pullRequests'][i]['source']['branch'], jsonData['detail'][0]['pullRequests'][i]['status']) 
                if jsonData['detail'][0]['pullRequests'][i]['status'] == "OPEN":
                    branch.append(jsonData['detail'][0]['pullRequests'][i]['source']['branch'])
            if branch:
                print(branch)
                testMerge(mergeBranch, branch)
                #merge_branches(versionName, branch)
            else:
                print(" There is no branches found to merge in this issue {}".format(issue['key']))
        else:
            print(" The issue {0} status({1}) not in Ready For Deployment. Skipping to merge".format(issue['key'], issueObject.fields.status))            
 
if __name__ == "__main__":
 
    login = Github('arun.venkat@aspiresys.com', 'Arun8600')
    mergeBranch = input("\nEnter the branch name to merge all the feature branches\n\n\t")
    check = [0,1]
 
    flag = int(input("Do you want create new branch?\n\tpress 1 for create\n\tpress 0 for skip\t"))
    while flag not in check:
        flag = int(input("You entered wrong option please re-enter\n\tpress 1 for create\n\tpress 0 for skip\t"))
    if flag:
        oldBranch = input("Enter the old branch name to create new branch\n\n\t")
        newBranch = input("Enter the new branch name to create from old branch {0}\n\n\t".format(oldBranch))
 
        createNewBranch(oldBranch, newBranch)
 
 
    jiraUname = b64decode(b'dmltYWwuZGhhbmFyYWpAemlmZml0eS5jb20=')
    jiraPassw = b64decode(b'VzI5ZDFkV0M=')
    jira = JIRA(options={'server': 'https://usesi1.atlassian.net'}, basic_auth=(jiraUname, jiraPassw))
    fetch_branches(mergeBranch, jira)
