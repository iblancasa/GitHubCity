from githubcity.ghuser import GitHubUser
import sys


def main(argv):
    user = GitHubUser(argv[0])
    user.getData()
    user.getRealContributions()
    print(user.export())

if __name__ == "__main__":
    main(sys.argv[1:])
