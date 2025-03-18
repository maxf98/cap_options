import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory():
    # Parameters
    num_points = 20  # Number of points
    x_spacing = 1  # Fixed horizontal distance
    y_offset = 0.2  # Maximum vertical offset

    # Generate points
    x = np.arange(num_points) * x_spacing
    y = np.random.uniform(-y_offset, y_offset, num_points)

    # Plot
    plt.figure(figsize=(8, 2))
    plt.plot(x, y, marker="o", linestyle="-", color="black")

    # Add labels with LaTeX subscripts
    plt.text(x[0], y[0] + 0.15, f"$s_{{{0}}}$", ha="center", fontsize=15)
    plt.text(
        x[num_points - 1],
        y[num_points - 1] + 0.15,
        f"$s_{{T}}$",
        ha="center",
        fontsize=15,
    )

    plt.ylim(min(y) - 0.2, max(y) + 0.3)  # Add padding above and below
    # Remove axes
    plt.axis("off")

    plt.show()


def generate_trajectory(num_points, x_spacing, y_offset, start_y=0):
    x = np.arange(num_points) * x_spacing
    ys = [start_y]
    for i in range(1, num_points):
        ys.append(ys[i - 1] + np.random.uniform(-y_offset, y_offset))

    return x, ys


def plot_behaviour():
    # Parameters
    num_trajectories = 5  # Number of positive trajectories
    num_points = 20  # Number of points per trajectory
    x_spacing = 1  # Fixed horizontal distance
    y_offset = 0.1  # Maximum vertical offset
    start_y_variation = 0.1  # Variation in starting y position
    opacity = 0.2  # Line and marker opacity

    # Create figure
    plt.figure(figsize=(8, 4))

    for t in range(3):
        x, y = generate_trajectory(
            num_points,
            x_spacing,
            0.05,
            np.random.uniform(-start_y_variation, start_y_variation),
        )

        # Plot with lower opacity
        plt.plot(x, y, marker="o", linestyle="-", color="black", alpha=1)

    neg_y_offset = 0.5
    for t in range(20):
        x, y = generate_trajectory(
            num_points,
            x_spacing,
            0.1,
            np.random.uniform(-start_y_variation, start_y_variation),
        )

        # Plot with lower opacity
        plt.plot(x, y, marker="none", linestyle="-", color="red", alpha=0.1)

    # Add padding by adjusting limits
    plt.xlim(x[0] - x_spacing, x[-1] + x_spacing)
    plt.ylim(-start_y_variation - y_offset - 0.5, start_y_variation + y_offset + 0.5)

    # Remove axes
    plt.axis("off")

    plt.show()


if __name__ == "__main__":
    plot_behaviour()
