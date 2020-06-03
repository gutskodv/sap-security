from sapsecurity.checks.manager import SAPSecurityAnalysis


def main():
    process = SAPSecurityAnalysis(do_log=True)
    process.start_analysis()


if __name__ == '__main__':
    main()
