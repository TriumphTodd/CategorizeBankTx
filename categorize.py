"""
bank_account_categorize.py
This script takes CSV files downloaded from your bank and applies a set of
rules to them in order to categorize them in ways useful for budgeting.
"""
# standard library imports
import csv
import sys
import logging
from logging.config import fileConfig
import fnmatch

# other modules
import yaml

def main():
    '''
    Main rule method - use 'globbing'
    https://docs.python.org/3.8/library/fnmatch.html
    TODO Split this into functions?
    '''
    rules = []
    txs = []

    # --------------------------------------------------------------------------
    #                              load configuration file
    # --------------------------------------------------------------------------

    try:
        log.info('Reading configuration file')
        with open('config.yml', 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        log.error("config.yml not found in script directory.")
        sys.exit(1)

    # --------------------------------------------------------------------------
    #                                 load rule file
    # --------------------------------------------------------------------------
    # TODO CSV dict writer for rules?
    try:
        with open(config['rule_file'], "r") as infile:
            rule_error = False
            expected_rule_cols = 7
            log.debug("------------------ Opening rule file ------------------")
            reader = csv.reader(infile)
            next(reader, None)  # skip the header
            rownum = 0

            for row in reader:
                rownum += 1
                if len(row) == expected_rule_cols:
                    rule = {}
                    rule['order'] = row[0]
                    rule['rule_type'] = row[1]
                    rule['pattern'] = row[2]
                    rule['tx_type'] = row[3]
                    rule['short_name'] = row[4]
                    rule['category1'] = row[5]
                    rule['category2'] = row[6]
                    msg = f"Rule:  {rule['rule_type']}=> " + \
                        f"{rule['pattern']} => " + \
                        f"{rule['short_name']} => " + \
                        f"{rule['tx_type']}"
                    log.debug(msg)
                    rules.append(rule)
                else:
                    msg = f"Expected {expected_rule_cols} columns but saw " + \
                        f"{str(len(row))} on row {str(rownum)}"
                    log.error()
                    log.error(str(row))
                    rule_error = True
            # stop running if the wrong number of columns are read
            if rule_error:
                log.error('Error reading rules')
                sys.exit(1)

    except FileNotFoundError:
        msg = f"{config['missing_rules_file']} not found in script directory."
        log.error(msg)
        sys.exit(1)

    # --------------------------------------------------------------------------
    #                       load input files
    # --------------------------------------------------------------------------

    try:
        input_files = config['input_files']
        for i in input_files.keys():
            input_file = config['input_files'][i]['filename']

            # load file_spec (column mapping)
            columns = config['input_files'][i]['columns'].split(',')
            log.debug("Columns: %s", columns)
            log.debug("++++++++++ Reading %s ++++++++++", input_file)
            with open(input_file, "r") as infile:
                reader = csv.reader(infile)
                next(reader, None)  # skip the header

                rownum = 0
                for row in reader:

                    rownum += 1
                    # there are always 8 data columns in my CSV file but only
                    # 7 column header values ??!?
                    if len(columns) != len(row):
                        log.error("Expected %i columns but saw %i on row %i in file %s", \
                            columns, len(row), rownum, input_file)
                        log.error(row)
                        sys.exit(1)

                    # Each row is a dictionary of column names/values
                    tx = {}
                    colnum = 0
                    for col in columns:
                        tx['account'] = config['input_files'][i]['account']
                        # log.debug("colnum=%i c=%s", colnum, col)
                        tx[col] = row[colnum]
                        colnum += 1
                    # log.debug('tx=' + str(tx))
                    txs.append(tx)

    except FileNotFoundError:
        log.error("%s not found in script directory.", input_file)
        sys.exit(1)


    # --------------------------------------------------------------------------
    #                    Apply rules to transactions
    # --------------------------------------------------------------------------

    # txs is a list of dictionaries
    tx_count = 0
    with open(config['missing_rules_file'], "w",
            newline='', encoding='utf-8') as missing_rules:
        missing = csv.writer(missing_rules, quoting=csv.QUOTE_MINIMAL)
        log.debug("---------- Running Rules ----------")
        for tx in txs:
            matched = False
            for rule in rules:
                if rule['rule_type'] == 'contains':
                    if fnmatch.fnmatch(tx['Description'], rule['pattern']):
                        if tx['Type'] == rule['tx_type']:
                            matched = True
                            # log.debug("Matched 'contains' rule: %s => %s", \
                            #    tx['Description'], rule['pattern'])
                            tx['rule_num'] = rule['order']
                            tx['short_name'] = rule['short_name']
                            tx['category1'] = rule['category1']
                            tx['category2'] = rule['category2']
                elif rule['rule_type'] == 'equals':
                    if rule['pattern'] == tx['Description']:
                        if tx['Type'] == rule['tx_type']:
                            matched = True
                            # log.debug("Matched 'equals' rule: %s => %s", \
                            #    tx['Description'], rule['pattern'])
                            tx['rule_num'] = rule['order']
                            tx['short_name'] = rule['short_name']
                            tx['category1'] = rule['category1']
                            tx['category2'] = rule['category2']
                else:
                    log.error("Unknown rule type")
                    log.error("Rule: %s", str(rule))
            if not matched:
                missing.writerow([tx['account'], tx['Description'], tx['Type']])
                tx['rule_num'] = 'None'
                tx['short_name'] = 'No Short Name'
                tx['category1'] = 'No Category 1'
                tx['category2'] = 'No Category 2'
            tx_count += 1
        log.info("Processed %i transactions", tx_count)


    # --------------------------------------------------------------------------
    # Output transactions
    # --------------------------------------------------------------------------

    # The config file lists the columns to output for each input file
    # (must be the same number for all files!)
    # Also, the output_header is a list of columns for the entire output file
    inputs = config['input_files']
    output_columns = {}
    for i in inputs.keys():
        # dictionary of config keys:  account (key) and output_columns (value)
        output_columns[config['input_files'][i]['account']] = \
            config['input_files'][i]['output_columns'].split(',')
        log.debug(str(output_columns))
    # output CSV enriched with categories

    with open(config['output_file'], 'w', newline='', encoding='utf-8') as out:
        outrows = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        header = config['output_header'].split(',')
        outrows.writerow(header)
        for tx in txs:
            # get output columns for each input file
            cols = output_columns[tx['account']]
            output_row = [tx['account']]
            for col in cols:
                output_row.append(tx[col])
            output_row.append(tx['rule_num'])
            output_row.append(tx['short_name'])
            output_row.append(tx['category1'])
            output_row.append(tx['category2'])
            log.debug(output_row)
            outrows.writerow(output_row)


if __name__ == '__main__':
    fileConfig('logging_config.ini')
    log = logging.getLogger(__name__)
    log.info("========== Starting up ==========")
    main()
