from githubcity.ghcity import GitHubCity
from os import environ
import sys


def main(argv):
    idGH = environ.get('GH_ID')
    secretGH = environ.get('GH_SECRET')
    configuration = {
        "excludedLocations": [],
        "excludedUsers": [],
        "intervals": [
            [
                "2008-01-01",
                "2015-12-30"
            ]
        ],
        "last_date": "2015-12-30",
        "locations": [
            "Ceuta"
            ],
        "name": "Ceuta"
            }
    ciudad = GitHubCity(idGH, secretGH, configuration)
    # ciudad.readConfigFromJSON(argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
