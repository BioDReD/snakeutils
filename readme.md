# snake-utils

Utilities for snakemake workflows 

## Installation

```sh
python -m pip install git+ssh://git@github.com/BioDReD/snakeutils.git
```

Depends on : (installed automatically)
- plotly >=6.0
- pandas >=1.0

## Useful functions and classes

- `SampleSheet` : a simple class to load the data from a samplesheet that can be passed to `bcl2fastq`. Usage : 

```py
sheet = SampleSheet("/path/to/samplesheet.csv")
fastqs_out = sheet.to_fastq()
```

- `params_to_CLI` : this function takes a dictionary of command line arguments and generates CLI args, with the common convention that single letter arguments are prefixed with a single dasg whereas multiletter arguments are prefixed with double dashes. 

## snakebench

Assuming you have defined benchmarks in your rules, this CLI can generate a html report summarizing these benchmarks.

In it's simplest form, `snakebench.py` executes as follows : 
```sh
snakebench.py /path/to/workflow/results/benchmarks /path/to/report.html
```

See an [example](./examples/bench_report.html)

Defaults : 

- if no `--log-file` is provided, rule names will be inferred to be the top dir/files in the benchmarks dir.
- `s` for x axis, aka execution time in seconds
- `max_pss` for the y axis, aka the max memory used by the process
- `mean_load` for the point size, aka CPU usage over time
- `max_pss` for sorting the summary table

```
usage: snakebench.py [-h] [--log-file LOG_FILE] [-x X] [-y Y] [--size SIZE] [--sort-by SORT_BY] bench report

positional arguments:
  bench                 Path to the benchmarks directory
  report                Path where the html report will be written

options:
  -h, --help            show this help message and exit
  --log-file LOG_FILE, -l LOG_FILE
                        Optionally provide a path to a snakemake execution log, to infer correct rule names if the automatic detection fails
  -x X                  Column to use for the x axis
  -y Y                  Column to use for the y axis
  --size SIZE, -s SIZE  Column to use for the point size
  --sort-by SORT_BY     Column to use for sorting in the report
```


## TODO

Re-write and optimise show_error_reasons in python