![](https://github.com/mgalushka/StocksTax/blob/master/content/StocksTax-Logo.png)

# StocksTax

StocksTax calculates capital gains using transactions and price
data from CSV files for shares transactions. Capital
gains are calculated according to section 104 holding; 30-day bed and
breakfasting; and same-day rules.

Guidance on tax calculation when selling shares: https://www.gov.uk/tax-sell-shares

## Disclaimer

**Do not rely on this software for accuracy. Anything provided by this software
does not constitute advice in any form. The software is provided "as is",
without warranty of any kind. Use at your own risk. See the LICENSE file for
more details.**

## Providing Data

Transaction data need to be provided in CSV files contained
within particular directories. Transactions are in `./gains`.

CSV files can be produced by any decent spreadsheet software. Spreadsheet
software can be used to manipulate exported price, exchange and wallet data into
the correct format.

Empty rows are allowed. Additional columns for comments etc. are allowed and
ignored.

Please see the `./examples` directory which contains an example of how data
should be provided.

### Capital Gain/Loss data

Buying selling shares and other acquisitions or disposals can be provided in
the `./gains` directory in as many CSV files as desired. The CSV files can be
named anything as long as they end in `.csv`.

Trades should be provided with the following columns:

| Column      | Description                                                               |
| ----------- | ------------------------------------------------------------------------- |
| DATE        | The date of the trade, acquistion and/or disposal formatted as YYYY-MM-DD |
| ASSET       | The name of the asset (stock index or company name)                       |
| AMOUNT      | Number of shares acquired or disposed                                     |
| PRICE       | Price in GBP paid/received per share                                      |
| FEE         | Fee paid for transaction in GBP                                           |

## Running Calculations

Please run `PYTHONPATH=. python3 pycryptax/__main__.py -h` for usage details.

When running a calculation you must either be in the directory containing the
`prices`, `income` and/or `gains` directories, or provide it using the `--dir`
option.

Calcuations are done for a particular period of time. The start and end dates
need to be provided in the `YYYY-MM-DD` format. For example, to calculate income
for the 2009-2010 tax year in the `./examples` directory:

    PYTHONPATH=. python3 pycryptax/__main__.py gain 2019-04-06 2020-04-05 -d ./examples

The following actions are allowed:

- **gain:** Produces the gain and loss for each asset and in total. Also
  displays the status of the section 104 holding at the end of the
calculation period.

## Acknowledgements

This program code is based on [PyCryptax](https://github.com/MatthewLM/PyCryptax) project by Matthew Mitchell [GitHub: @MatthewLM](https://github.com/MatthewLM)
