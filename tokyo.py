
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import mplcursors  # Import mplcursors library for hover annotations

# Function to detect anomalies using Z-score
def detect_anomalies(data, threshold=3):
    mean = np.mean(data)
    std = np.std(data)
    z_scores = np.abs((data - mean) / std)
    anomalies = z_scores > threshold
    return anomalies

# Function to plot the original graph in the main window
def plot_original_graph(df, primary_parameters, secondary_parameters, frequency):
    # Check if any primary parameters are selected as secondary parameters
    common_params = set(primary_parameters).intersection(set(secondary_parameters))
    if common_params:
        messagebox.showwarning("Warning", f"The following parameters are selected for both primary and secondary axes: {', '.join(common_params)}")
        return

    # Create a new figure and axis for the main plot
    fig, ax = plt.subplots()

    # Plot the primary parameters on the primary axis
    for parameter in primary_parameters:
        ax.plot(df.index / frequency, df[parameter], label=f"Primary: {parameter}")

    # Set up the secondary axis
    ax2 = ax.twinx()

    # Plot the secondary parameters on the secondary axis
    for parameter in secondary_parameters:
        ax2.plot(df.index / frequency, df[parameter], label=f"Secondary: {parameter}", linestyle='dashed')

    # Set labels and legends for the main plot
    ax.set_xlabel(f'Index / {frequency}')
    ax.set_ylabel('Primary Axis Values')
    ax2.set_ylabel('Secondary Axis Values')
    ax.set_title('Graph with Selected Parameters on Primary and Secondary Axis')

    # Combine the indices from both primary and secondary parameters for setting the x-axis range
    all_indices = df.index / frequency

    # Set the same x-axis range for both plots
    ax.set_xlim(min(all_indices), max(all_indices))
    ax2.set_xlim(min(all_indices), max(all_indices))

    # Find the y-axis limits for primary and secondary parameters in the main plot
    y_min = min(df[primary_parameters + secondary_parameters].values.min(), df[primary_parameters + secondary_parameters].values.min())
    y_max = max(df[primary_parameters + secondary_parameters].values.max(), df[primary_parameters + secondary_parameters].values.max())

    # Set the same y-axis limits for both plots
    ax.set_ylim(y_min, y_max)
    ax2.set_ylim(y_min, y_max)

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines2, labels2, loc='upper right')
    ax.legend(lines, labels, loc='upper left')

    # Create the Tkinter canvas to display the main plot
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add the navigation toolbar to the Tkinter GUI for the main plot
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Deiconify the plot window to display the main plot
    plot_window.deiconify()

# Function to plot the anomaly points in a separate window with annotations for coordinates
def plot_anomaly_points(df, primary_parameters, secondary_parameters, frequency, anomaly_alpha=0.7):
    # Combine primary and secondary parameters for anomaly detection
    selected_parameters = primary_parameters + secondary_parameters

    # Filter out invalid parameters
    valid_parameters = [param for param in selected_parameters if param in df.columns]

    if not valid_parameters:
        messagebox.showwarning("Warning", "No valid parameters selected for anomaly detection.")
        return

    # Create a new figure and axis for the anomalies plot
    fig_anomalies, ax_anomalies = plt.subplots()

    # Plot the selected parameters on the anomalies plot
    for parameter in valid_parameters:
        anomalies = detect_anomalies(df[parameter])
        ax_anomalies.scatter(df.index[anomalies] / frequency, df[parameter][anomalies], color='red', label=f"Anomaly ({parameter})", marker='x', alpha=1.0)

    # Set labels and legends for the anomalies plot
    ax_anomalies.set_xlabel(f'Index / {frequency}')
    ax_anomalies.set_ylabel('Anomaly Values')
    ax_anomalies.set_title('Anomalies Detected')

    # Combine the indices from both primary and secondary parameters for setting the x-axis range
    all_indices = df.index / frequency

    # Set the same x-axis range for both plots
    ax_anomalies.set_xlim(min(all_indices), max(all_indices))

    # Find the y-axis limits for primary and secondary parameters in the anomaly plot
    y_min = min(df[selected_parameters].values.min(), df[selected_parameters].values.min())
    y_max = max(df[selected_parameters].values.max(), df[selected_parameters].values.max())

    # Set the same y-axis limits for both plots
    ax_anomalies.set_ylim(y_min, y_max)

    lines, labels = ax_anomalies.get_legend_handles_labels()
    ax_anomalies.legend(lines, labels, loc='upper right')

    # Use mplcursors to add annotations for coordinates when hovering over anomaly points
    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(f'({sel.target[0]:.2f}, {sel.target[1]:.2f})'))

    # Create the Tkinter canvas to display the anomalies plot
    canvas_anomalies = FigureCanvasTkAgg(fig_anomalies, master=plot_window_anomalies)
    canvas_anomalies.draw()
    canvas_anomalies.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add the navigation toolbar to the Tkinter GUI for the anomalies plot
    toolbar_anomalies = NavigationToolbar2Tk(canvas_anomalies, plot_window_anomalies)
    toolbar_anomalies.update()
    canvas_anomalies.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Set the window opacity (alpha)
    plot_window_anomalies.attributes('-alpha', anomaly_alpha)

    # Adjust the size and position of the anomaly window to overlap the original graph window
    original_graph_geometry = plot_window.geometry()
    plot_window_anomalies.geometry(original_graph_geometry)

    # Deiconify the anomalies plot window to display the anomalies plot
    plot_window_anomalies.deiconify()

# Function to prompt the user to select primary parameters
def select_primary_parameters(df, all_parameters):
    # Create a label and drop-down list for primary parameters
    primary_label = tk.Label(root, text="Select Primary Parameters (Hold Ctrl for multiple selection):")
    primary_label.pack()

    primary_variables = tk.StringVar(root, value=all_parameters)
    primary_dropdown = tk.Listbox(root, listvariable=primary_variables, selectmode=tk.MULTIPLE, exportselection=False)
    primary_dropdown.pack()

    # Button to continue to secondary parameter selection
    continue_button = tk.Button(root, text="Continue", command=lambda: select_secondary_parameters(df, primary_dropdown.curselection(), all_parameters))
    continue_button.pack(pady=10)

# Function to prompt the user to select secondary parameters
def select_secondary_parameters(df, primary_indices, all_parameters):
    # Get the selected primary parameters
    primary_parameters = [all_parameters[index] for index in primary_indices]

    # Create a label and drop-down list for secondary parameters
    secondary_label = tk.Label(root, text="Select Secondary Parameters (Hold Ctrl for multiple selection):")
    secondary_label.pack()

    secondary_variables = tk.StringVar(root, value=all_parameters)
    secondary_dropdown = tk.Listbox(root, listvariable=secondary_variables, selectmode=tk.MULTIPLE, exportselection=False)
    secondary_dropdown.pack()

    # Button to plot the original graph
    frequency = 256  # Default frequency value, can be modified by the user
    plot_button = tk.Button(root, text="Plot Original Graph", command=lambda: plot_original_graph(df, primary_parameters, [secondary_dropdown.get(index) for index in secondary_dropdown.curselection()], frequency))
    plot_button.pack(pady=10)

    # Button to plot the anomaly points
    plot_anomalies_button = tk.Button(root, text="Plot Anomaly Points", command=lambda: plot_anomaly_points(df, primary_parameters, [secondary_dropdown.get(index) for index in secondary_dropdown.curselection()], frequency))
    plot_anomalies_button.pack(pady=10)

    # Button to select frequency
    def select_frequency():
        nonlocal frequency
        frequency_window = tk.Toplevel(root)
        frequency_window.title("Select Frequency")

        def set_frequency(value):
            nonlocal frequency
            frequency = value
            frequency_window.destroy()

        frequencies = [256, 64, 32, 100, 200]
        for freq in frequencies:
            rb = tk.Radiobutton(frequency_window, text=f"{freq}", value=freq, command=lambda freq=freq: set_frequency(freq))
            rb.pack(anchor=tk.W)

    frequency_button = tk.Button(root, text="Select Frequency", command=select_frequency)
    frequency_button.pack(pady=10)

# Function to browse and read the CSV file
def browse_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    df = pd.read_csv(file_path)
    column_names = df.columns.tolist()

    select_primary_parameters(df, column_names)



# Create the main Tkinter GUI window
root = tk.Tk()
root.title("Select Parameters")

# ... (Same as before)
browse_button = tk.Button(root, text="Browse CSV File", command=browse_csv_file)
browse_button.pack(pady=10)

# Create a separate window for the main plot
plot_window = tk.Toplevel(root)
plot_window.title("Main Graph")
plot_window.withdraw()  # Hide the window initially

# Create a separate window for the anomalies plot
plot_window_anomalies = tk.Toplevel(root)
plot_window_anomalies.title("Anomalies Plot")
plot_window_anomalies.withdraw()  # Hide the window initially

root.mainloop()
