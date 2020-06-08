import argparse
from sapsec.checks.manager import SAPSecurityAnalysis


def create_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-r', '--rules', action="store", help='Security checks configuration file')
    return arg_parser


def start_check(rules_file=None):
    process = SAPSecurityAnalysis(do_log=True)
    process.set_rules_file(rules_file)
    process.start_analysis()


def main():
    parser = create_parser()
    namespace = parser.parse_args()
    if namespace.rules:
        start_check(namespace.rules)
    else:
        start_check()


if __name__ == '__main__':
    main()
