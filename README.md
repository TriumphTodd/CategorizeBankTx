# Categorize Bank Transaction Files
# script name: categorize.py

## Purpose

The purpose of this script is to take comma-separated value files downloaded 
from your bank for your personal accounts (checking, savings, etc.) and apply a 
set of rules to them in order to categorize them into groups useful for 
making a personal budget.

The output is also a CSV file but you can import that into a spreadsheet and 
create pivot tables and other summary reports.  I may later make some report
scripts that do that and maybe make charts.

I used the CSV format from my bank but I assume most banks will have a pretty
similar format.  It seems like the columns are mostly similar to the OFX format
used for personal finance applications.

Sample data is included for illustration purposes.  I removed all identifying
transaction numbers as well as changed transaction amounts and other details
in many cases.  No, I don't live in Buttzville, NJ.  It is a real place though.

## Files

- *categorize.py* - The script itself

- *config.yml* - Contains the main configuration settings

- *logging_config.ini* - Logging configuration file

- *checking-conda-env.yml* - Configuration file for conda environment

- *rules_test.csv* - Test rule file 

- *missing_rules.csv* - Output file that shows data records that were not
    processed by a rule.  Useful for refining the rule file.

- *checking.csv* - Sample test data

- *savings.csv* - Sample test data

- *credit_card.csv* - Sample test data

- *run_pylint.bat* - Windows batch file to run the python linter which outputs 
    text to *pylint_output.txt*.  The tool reports syntax errors and bad coding
    practices.  Not necessary to run the script, only if you're developing.

- *README.md* - This documentation file

## Setup

1. Clone github repository into a folder
    - Get a terminal/command window and change to a folder that will hold the code
    - Type this command into a terminal window: `git clone https://github.com/TriumphTodd/YOUR-REPOSITORY`
    - Reference: [Github Link](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

2. Create conda environment with all the required packages to run the script
    - Assumes the Anaconda python environment is installed 
        [anaconda.com](https://www.anaconda.com/)
    - Enter this command in a terminal: `conda env create --file checking-conda-env.yml`
    - Reference:  [Anaconda Link](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
    - If you're not using Anaconda, it will be difficult to convert the *conda*
        file into a format usable by *pip* or *pipenv*.  It's not impossible, 
        and google away, but I won't cover it here.

3. Write the configuration file for your own files
    - See the **Writing the configuration file** section below

## Usage

1. Activate the conda environment
    - Command line:  `conda activate checking`

2. Run the script using the test data
    - Command line:  `python categorize.py`

3. Review transactions not captured by rules (e.g. Autozone in the test data)
    - See file *missing_rules.csv*
    - Also look at the log file (*categorize.log*) and look for processing errors

4. Update rules
    - See **Writing Rules** section below

5. Keep writing rules until everything is classified.  It will take a while.  :-(

6. Review output file
    - See *output.csv*

7. Import output file into spreadsheet and budget away!

## Writing the configuration file

The main configuration file for this script is *config.yaml*.  YAML is a 
simple and easy to use configuration file format:  [Python Website](https://wiki.python.org/moin/YAML)

Essentially, it lists key/value pairs separated by colons:  `rule_file: 'rules_test.csv'`
It also has nesting, which I will explain below.

The first main settings are as follows:

1. *rule_file*: the file containing the rules used to categorize the transactions

2. *missing_rules_file*:  lists transactions not covered by a rule

3. *output_file*: a filename to store the output (*.csv)

4. *output_header*: This is a quoted, comma-separated list of the columns used
    in the *output.csv* file.  It has no dependency on the input files but
    should be consistent with the *output_columns* data listed below as well
    as the columns output by the script.

The next section lists nested data for each input file the script will
process.  Each input file is defined in its own sub-section.

Multiple input files with transactions are possible.  I listed three in 
the test data.  The main thing is to coordinate the columns sent into the
output file.

1. *input_files*:  This line has no value to it, only the key.
    It is just the start of the section.

2. *checking*: This key identifies the file used in the config file.
    It is the sub-section header and can be any text you like. Must have **one**
    level of indentation.

3. *filename*: The CSV file to process, e.g. (*'checking.csv'*).
    Must have **two** levels of indentation.

4. *columns*: A comma-separated lists of the column headers in the CSV file.
    Must have **two** levels of indentation.

5. *account*: The name of the input file that will go in the output file. 
    Name it whatever you like. Must have **two** levels of indentation.

6. *rule_column*: This is the column in the CSV file with the text that is used 
    to process the rules.  (e.g. *'Description'*) Must have **two** levels of indentation.

7. *tx_type_column*: This column determines the type of transaction the rule 
    must match (e.g. the *'Type'* column must be *'DEBIT_CARD'*)
    Must have **two** levels of indentation.

8. *output_columns*: A quoted, comma-separated list of the columns in the input 
    CSV file that will eventually be sent into the output file. 
    **Make sure the column list is consistent between input files**
    Must have **two** levels of indentation.
    (e.g. *'Posting Date,Description,Amount,Type,Check or Slip #'*)

9. Repeat items 2-8 for each file to be processed.

## Writing Rules

There are two types of rules that will categorize the transactions.  They are 
both stored in the rule CSV file identified in the configuration file.

Probably the best way to start writing the rules is to run the script once on
your transaction files and see which  transactions fall out from the rule file.  
It will probably be most or all transactions.  They will be listed in the 
*'missing_rules.csv'* file.

### Rule Types

1. *'contains'*: This type of rule uses 'globbing', or 'wildcard' characters 
    that you can use to match groups of transactions.

    For example, the below rule will match both transaction descriptions in one go:<br/>
        Rule: ACME*<br/>
        Description: 'ACME 1234 BUTTZVILLE NJ              654321  06/25'<br/>
        Description: 'ACME 1234 BUTTZVILLE NJ              987654  11/20'<br/>

    This is the most flexible type of rule but doing an entire checking account
    download with this will be very time consuming.  It's best used for recurring
    transactions so that you don't have to keep doing the second type of rule.

    See this link for more information on the pattern matching capabilities:
    [Python Documentation](https://docs.python.org/3.8/library/fnmatch.html)

    It would of course be possible to have transactions matched by regular
    expressions but I personally found the wildcards much easier to work with.

2. *'equals'*: This type of rule will match the transaction description (or
    whatever the column is called) exactly and apply the categories as per
    the rule.

    This is best used for non-recurring transactions and after you've created
    as many 'contains' rules as you are willing to spend time on.

    The fastest way to create this type of rule is to take the descriptions 
    and transaction types from the *missing_rules.csv* file, copy them into a 
    spreadsheet, and create the equals rules from there.

### Rule Columns

The columns are as follows:

- *'order'*: I number the rules sequentially.  This number will appear in the 
    output for reference purposes.

- *'rule_type'*: Either 'contains' or 'equals'

- *'pattern'*: if it's a 'contains' rule, the wildcard pattern to match in 
    the transaction description

- *'tx_type'*: The transaction type listed in the input file, e.g. *'DEBIT_CARD'*

- *'short_name'*: This is the friendly name of the transaction that will
    appear in the output file, e.g. *'Starbucks'*.

- *'category1'*: First category applied to the transaction.

- *'category2'*:  Second category applied to the transaction.

More categories are certainly possible but it will take editing the code and
the configuration files.

### Convert Readme file to html
- Use this command line:  `python -m markdown README.md`
- Alternatively, use VS Code extension 'Markdown PDF'


### Command lines to manage conda environment
Default command to export an environment (not OS-specific)
`conda env export --name checking > checking-conda-env.yml`

Command to export an OS-specific file
`conda list --explicit > pkgs.txt`

