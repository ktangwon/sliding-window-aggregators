#!/usr/bin/env python3

import matplotlib.pyplot as plt
import process_utility as u
from run_bulk_evict_latency import functions, base_window_sizes, bulk_sizes
import math
import process_bulk_data_latency as pbdl
import numpy as np

aggregators = [
    "bfinger4",
    "bfinger8",
    "nofl_bfinger4",
    "nofl_bfinger8",
]
windows = base_window_sizes
bulk_sizes = [4096]

def get_screen_name(name: str) -> str:
    allocator, algo = name.split('-')
    NOFL_PREFIX = "nofl_"
    nofl = False
    if algo.startswith(NOFL_PREFIX):
        nofl = True
        algo = algo[len(NOFL_PREFIX):]
    qualifiers = []
    algo = algo.replace("bfinger", "b_fiba")
    if allocator == "mimalloc":
        qualifiers.append("mm")
    else:
        qualifiers.append("libc")
    if nofl:
        qualifiers.append("nofl")
    return f"{algo} ({', '.join(qualifiers)})"

def make_violin_graph(data, aggs_sorted, name, title, preamble, func, use_custom_y=False, force_bottom=True):
    graph = plt.figure(figsize=(6, 0.75 * 4))
    ax = graph.add_subplot(111)
    ax.set_title(title)
    ax.set_ylabel("processor cycles")
    ax.semilogy()
    all_latencies = []
    all_perc99 = []
    all_perc99999 = []
    all_median = []
    all_mean = []
    pos = range(1, len(aggs_sorted) + 1)
    for agg in aggs_sorted:
        latencies = np.array(data[agg], dtype=np.uint64)
        all_latencies.append(latencies)
        all_perc99.append(np.percentile(latencies, 99.9))
        all_perc99999.append(np.percentile(latencies, 99.999))
        all_median.append(np.median(latencies))
        all_mean.append(np.average(latencies))

    VERT_LINE = "#33a"
    RED_DARK = "#850e00"
    LIGHT_GRAY = "#becae4"
    GREY="#555"
    DARK_GREY="#333"
    parts = ax.violinplot(all_latencies, pos, points=250, showmedians=False, showextrema=False)
    for p in parts["bodies"]:
        p.set_facecolor(LIGHT_GRAY)
        p.set_edgecolor(GREY) 
        p.set_linewidth(1)
        

    ax.hlines(all_perc99, xmin=[x - 0.1 for x in pos], xmax=[x + 0.1 for x in pos], linewidth=1, color=VERT_LINE)
    for x, y in zip(pos, all_perc99):
        plt.text(x + 0.15, y, "99.9%", va="center", fontsize=8)

    ax.hlines(all_perc99999, xmin=[x - 0.1 for x in pos], xmax=[x + 0.1 for x in pos], linewidth=1, color=VERT_LINE)
    
    for x, y in zip(pos, all_perc99999):
        plt.text(x + 0.15, y, "99.999%", va="center", fontsize=8)

    ax.hlines(all_median, xmin=[x - 0.15 for x in pos], xmax=[x + 0.15 for x in pos], linewidth=2, color=VERT_LINE)

    ax.scatter(pos, all_mean, s=25, color=RED_DARK, zorder=3)
    
    ax.vlines(pos, ymin=[np.min(l) for l in all_latencies], 
                   ymax=[np.max(l) for l in all_latencies], color=DARK_GREY, linewidth=1.25, capstyle="round")
    if force_bottom:
        plt.ylim(bottom=1)
    if use_custom_y:
        ax.set_yticks(y_ticks)
        ax.yaxis.set_minor_locator(LogLocator())
        plt.ylim(top=max_yaxis[func])

    plt.setp(
        ax,
        xticks=[x for x in range(1, 1+len(aggs_sorted))],
        xticklabels=[get_screen_name(agg) for agg in aggs_sorted],
    )
    graph.autofmt_xdate()
    graph.savefig(
        "figures/" + preamble + "_violin_" + name + ".pdf", bbox_inches="tight"
    )
    plt.close(graph)

def make_bulk_evict_latency_plots():
    file_preamble = 'latency_bulk_evict_opevict'

    f = 'geomean'
    for w in windows:
        for b in bulk_sizes:
            data = {}
            exp_name = f + '_w' + str(w) + f'_d0_b{b}'
            window_size = '$2^{' + str(int(math.log(w, 2))) + '}$'
            display_bulk_size = '$2^{' + str(int(math.log(b, 2))) + '}$'
            exp_title = f + ', window ' + window_size + ', bulk_size ' + display_bulk_size
            exp_title = f 
            for flav in ["mimalloc", "vanilla"]:
                for agg in aggregators:
                    filespec = 'results-ablation/' + f"{flav}-" + file_preamble + '_' + agg + '_' + exp_name + '.txt'
                    tag = f"{flav}-{agg}"
                    data[tag] = u.read_latency_data(filespec)

            preamble = "ablation-bulkevict-latency"
            make_violin_graph(data, sorted(list(data.keys())), exp_name, exp_title, preamble, f, force_bottom=False)
            
def main():
    u.create_figures_dir()
    u.set_fonts()
    plt.rcParams['xtick.labelsize'] = 12

    make_bulk_evict_latency_plots()
if __name__ == "__main__":
    main()
