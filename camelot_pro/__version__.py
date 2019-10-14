VERSION = (1, 0, 0)
PRERELEASE = None  # "alpha", "beta" or "rc"
REVISION = None


def generate_version(version, prerelease=None, revision=None):
    version_parts = [".".join(map(str, version))]
    if prerelease is not None:
        version_parts.append("-{}".format(prerelease))
    if revision is not None:
        version_parts.append(".{}".format(revision))
    return "".join(version_parts)


__title__ = "CamelotPro"
__description__ = "CamelotPro is a layer on camelot-py library to extract tables from Scan PDFs and Images."
__url__ = "https://github.com/ExtractTable/camelotpro"
__version__ = generate_version(VERSION, prerelease=PRERELEASE, revision=REVISION)
__author__ = "Akshowhini"
__author_email__ = "brain@extracttable.com"
__license__ = "GPL-3.0"
