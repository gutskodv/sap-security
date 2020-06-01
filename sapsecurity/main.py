from sapsecurity.checks.manager import MainProcess


def main():
    process = MainProcess('Security checks processing', do_log=True)
    process.sap_login()
    if process.sap_session:
        process.add_checks()
        process.execute_all()
        process.create_report()


if __name__ == '__main__':
    main()