#!/usr/bin/env python3

from pathlib import Path
from datetime import time 
import plotly.express as px
import pandas as pd

TEMPLATE = """
<!DOCTYPE html>
<head>
    <style>
        body { font-family: "Arial", sans-serif; line-height: 1.6; color: #333; background-color: #fdfdfd; margin: 40px; padding: 0;}
        h1 { font-size: 2em; font-weight: bold; color: #003366; border-bottom: 3px solid #003366; padding-bottom: 5px; margin-top: 30px;}
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 1em; text-align: left; border: 1px solid #ddd; background-color: #fff;}
        th,td { padding: 10px; border: 1px solid #ccc;}
        th { background-color: #e6f0ff; color: #003366; font-weight: bold;}
        tr:nth-child(even) {background-color: #f9f9f9;}
    </style>
</head>
<body>
    <h1>Benchmarks for a snakemake pipeline</h1>
    <p>See the graph below for run metrics. You can pan and zoom on the graph to make busy areas more readable.</p>
    PLACEHOLDER_FIG
    <h1>Median values for each rule</h1>
    See <a href="https://stackoverflow.com/a/66872577">stackoverflow</a> for the meaning of each column
    PLACEHOLDER_TABLE
</body>
"""

def load_benchmark(f:Path) : 
    """
    Given a snakemake benchmark file (tsv), returns a dict of the values, with appropriate type
    """
    types = {
        "h:m:s" : lambda s : time(*[int(x) for x in s.split(":")])
    }


    lines = [l.split("\t") for l in f.read_text().split("\n") if l]
    if len(lines) != 2 :
        raise ValueError(f"Unexpected number of lines in file {f} : {len(lines)} instead of 2")
    
    return {key:types.get(key, float)(val) for key, val in zip(lines[0], lines[1])}

def get_rule_name_from_file(f:Path, known_names=set(), parent=None) : 
    """
    Given a path to a benchmark file, will return the name of the rule for this benchmark, as well as the relative path to help interpretation of the data
    - known_names : a set of rule names that will ensure correct naming. 
    If this argument is not given, the rule name will be inferred to be the the first level dir/file below the given parent. 
    
    - parent : the path to the folder that contains all benchmarks.
    If no parent is given, the full path must contain a "benchmarks" folder that will be used as parent.
    """

    if parent is None : 
        if "benchmarks" not in str(f) : 
            raise ValueError(f"No directory named 'benchmarks' in {f}, please pass a valid Path to the 'parent' argument")
        parts = []
        for p in f.parts : 
            parts.append(p)
            if p == "benchmarks" : 
                break
        parent = Path("/".join(parts))

    relative = f.relative_to(parent)
    for p in relative.parts : 
        if p in known_names : 
            return p, str(relative)
        
    return relative.parts[0], str(relative)


def get_benchmarks(path:Path, known_names=set(), rules=[], _parent=None) :
    """
    Given a path where snakemake benchmarks are stored, will recursively descend the directories and generate an easily parseable object.
    """ 
    if _parent is None : 
        _parent = path

    for item in path.iterdir() : 
        if item.is_dir() : 
            get_benchmarks(item, rules=rules, _parent=_parent)
        elif item.is_file() and item.name.endswith("tsv"): 
            bench = load_benchmark(item) 
            rule, relative_path = get_rule_name_from_file(item, parent=_parent, known_names=known_names)
            bench["relative_path"] = relative_path
            bench["rule"] = rule.replace(".tsv", "")
            rules.append(bench)
        else : 
            pass

    return rules

def create_report(bench_path, report_path, known_names=set(), x="s", y="max_pss", size="mean_load", sort_by="max_pss") : 
    print(f"Parsing benchmarks in {bench_path}...")
    benchs = Path(bench_path)
    benchs = get_benchmarks(benchs, known_names=known_names)
    df = pd.DataFrame(benchs)

    stats = df.groupby("rule").median(numeric_only=True).reset_index()
    fig = px.scatter(
        df,
        x=x, 
        y=y, 
        color="rule", 
        hover_data=list(df.columns), 
        size=size,
        render_mode=""
    )

    for x, y, text in zip(stats["s"], stats["max_pss"], stats["rule"]) : 
        fig.add_annotation(
            x=x,y=y, text=text, showarrow=False,
            font=dict(size=15)
    )
    fig.update_layout(
        autosize=False,
        width=1200,
        height=1200,
        showlegend=False,
    )

    with open(report_path, "w+") as fp : 
        fp.write(
            TEMPLATE.replace(
                "PLACEHOLDER_FIG", fig.to_html(include_plotlyjs=True, full_html=False)).replace(
                "PLACEHOLDER_TABLE", stats.sort_values(sort_by).to_html(index=None)
            )
        )

def get_rule_names_from_log_file(logfile) : 
    logfile = Path(logfile)
    rules = set()

    with open(logfile) as fp : 
        rule_section = False
        for line in fp :
            if rule_section and not (line.startswith("--") or line.strip() == ""): 
                rules.add(line.split()[0])
            
            if line.startswith("Job stats") : 
                rule_section = True
            if rule_section and line.strip() == "" : 
                rule_section = False

    print(f"Found {len(rules)} rules in '{logfile.name}' : [{','.join(list(rules)[:5])}...]")

    return rules

if __name__ == "__main__"  :
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("bench", help="Path to the benchmarks directory")
    parser.add_argument("report", help="Path where the html report will be written")
    parser.add_argument("--log-file", "-l", help="Optionally provide a path to a snakemake execution log, to infer correct rule names if the automatic detection fails")
    parser.add_argument("-x", help="Column to use for the x axis", default="s")
    parser.add_argument("-y", help="Column to use for the y axis", default="max_pss")
    parser.add_argument("--size", "-s", help="Column to use for the point size", default="mean_load")
    parser.add_argument("--sort-by", help="Column to use for sorting in the report", default="max_pss")

    args = parser.parse_args()

    if args.log_file is not None : 
        rule_names = get_rule_names_from_log_file(args.log_file)
    else :
        rule_names = set()

    create_report(args.bench, args.report, rule_names, x=args.x, y=args.y, size=args.size, sort_by=args.sort_by)

    print(f"Succesfully written report to {args.report}")
