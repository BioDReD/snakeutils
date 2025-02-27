# snake-utils

Utilities to analyse snakemake workflow past executions

## snakebench

Assuming you have defined benchmarks in your rules, this CLI can generate a html report summarizing these benchmarks.

In it's simplest form, `snakebench.py` executes as follows : 
```sh
snakebench.py /path/to/workflow/results/benchmarks /path/to/report.html
```

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