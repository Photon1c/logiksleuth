#Create A Random Galton Board of Probability Ranges
import random
import matplotlib.pyplot as plt



def simulate_galton_board(num_balls, num_slots):
    slots = [0] * (num_slots + 1)
    for i in range(num_balls):
        pos = 0
        for j in range(num_slots - 1):  # change to num_slots-1
            if random.random() < 0.5:
                pos += 1
        slots[pos] += 1 if pos <= num_slots else 0  # add check for pos > num_slots
    return slots


def print_probability_ranges(num_balls, num_slots):
    slots = simulate_galton_board(num_balls, num_slots)
    total_balls = sum(slots)
    prob_ranges = []
    start_prob = 0
    for count in slots:
        end_prob = start_prob + (count / total_balls)
        prob_ranges.append((start_prob, end_prob))
        start_prob = end_prob
    print(f"Probability Ranges for {num_balls} balls and {num_slots} slots:")
    for i, prob_range in enumerate(prob_ranges):
        print(f"Slot {i}: {prob_range[0]:.2f} - {prob_range[1]:.2f}")
    
    fig, ax = plt.subplots()
    ax.bar(range(num_slots+1), slots, width=0.8, align='center', color='blue')
    ax.set_xlabel('Slot')
    ax.set_ylabel('Number of Balls')
    ax.set_title(f"Galton Board Results for {num_balls} Balls and {num_slots} Slots")
    plt.savefig(f"galton_board_{num_balls}_{num_slots}.png")
    plt.show()

# Example usage:
num_balls = 10000
num_slots = 20
print_probability_ranges(num_balls, num_slots)
