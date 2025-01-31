import os
import re
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def parse_log_file(file_name, patterns):
    data = {label: [] for label in patterns.keys()}

    print(f"Processing file: {file_name}")
    with open(file_name, 'r') as file:
        for line in file:
            for label, (pattern, axis, color) in patterns.items():
                match = re.search(pattern, line)
                if match:
                    timestamp = datetime.strptime(match.group(1), '%d/%m/%y %H:%M:%S')
                    value = int(match.group(2))
                    data[label].append((timestamp, value))
                    print(f"{label}: {line.strip()}")

    for label in data:
        print(f"File {file_name}: {label} entries: {len(data[label])}")
    return data

def plot_and_save_data(file_name, data, patterns, output_filename):
    fig, ax_left = plt.subplots(figsize=(12, 6))
    ax_right = ax_left.twinx()

    for label, entries in data.items():
        if entries:
            timestamps, values = zip(*sorted(entries))
            axis = patterns[label][1]
            color = patterns[label][2]
            if axis == 'left':
                ax_left.plot(timestamps, values, label=label, color=color)
                ax_left.scatter(timestamps, values, s=10, color=color)  # s=10 for smaller markers
            elif axis == 'right':
                ax_right.plot(timestamps, values, label=label, color=color)
                ax_right.scatter(timestamps, values, s=10, color=color)  # s=10 for smaller markers

    ax_left.set_xlabel('Time')
    ax_left.legend(loc='upper left')
    ax_right.legend(loc='upper right')
    ax_left.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y %H:%M:%S'))
    ax_left.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax_left.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_filename)

# Example usage
patterns = {
    'Retry Count': (r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*Bulk request failed. attempt = ([0-9])', 'right', 'red'),
    'Rate Limit': (r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*Current rate limit for bulk request is (\d+) documents/sec', 'left', 'blue'),
    'Estimated Rate': (r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*Current estimated rate is (\d+) documents/sec', 'left', 'green')
}

def main():
    # Check if log file names are provided as command-line arguments
    if len(sys.argv) < 2:
        print("Please provide at least one log file name as a command-line argument.")
        sys.exit(1)

    # Get log file names from command-line arguments
    log_files = sys.argv[1:]

    # Parse log files, extract data, and create individual graphs
    for file_name in log_files:
        data = parse_log_file(file_name, patterns)
        
        # Generate output filename in the same directory as the input file
        output_filename = os.path.splitext(file_name)[0] + "_rate_analysis.png"
        
        plot_and_save_data(file_name, data, patterns, output_filename)

if __name__ == "__main__":
    main()