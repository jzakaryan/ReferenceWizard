import logging

logging.basicConfig(filename='wizard.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
echo_logs_in_console = True


def log_info(message):
    logging.debug(message)
    if echo_logs_in_console:
        print(message)


def log_list(list):
    result_string = ""
    for record in list:
        result_string += "\t" + record + "\n"
    log_info(result_string)
