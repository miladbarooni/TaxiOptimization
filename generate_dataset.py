#!/usr/bin/env python
"""
Generate synthetic taxi trip datasets for testing.

This script generates random trip data with realistic constraints:
- Trips occur between 6:00 AM and 10:00 PM
- Trip durations range from 10 to 60 minutes
- Locations are randomly assigned from the available locations
"""

import random
import argparse
import os


def generate_trips(num_trips, num_locations=10, seed=42):
    """
    Generate synthetic trip data.

    Args:
        num_trips: Number of trips to generate
        num_locations: Number of locations (excluding depot at index 1)
        seed: Random seed for reproducibility

    Returns:
        List of trips as (start_time, end_time, pickup, dropoff)
    """
    random.seed(seed)
    trips = []

    # Operating hours: 6:00 AM to 10:00 PM (360 to 1320 minutes)
    min_start = 6 * 60   # 6:00 AM in minutes
    max_start = 20 * 60  # 8:00 PM in minutes (allow 2 hours for last trips)

    for _ in range(num_trips):
        # Random start time
        start_minutes = random.randint(min_start, max_start)

        # Trip duration: 10 to 60 minutes
        duration = random.randint(10, 60)
        end_minutes = start_minutes + duration

        # Convert to HHMM format
        start_time = (start_minutes // 60) * 100 + (start_minutes % 60)
        end_time = (end_minutes // 60) * 100 + (end_minutes % 60)

        # Random pickup and dropoff (locations 2 to num_locations, excluding depot at 1)
        pickup = random.randint(2, num_locations)
        dropoff = random.randint(2, num_locations)
        while dropoff == pickup:
            dropoff = random.randint(2, num_locations)

        trips.append((start_time, end_time, pickup, dropoff))

    # Sort by start time
    trips.sort(key=lambda x: x[0])

    return trips


def save_trips(trips, filepath):
    """Save trips to file in the expected format."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        f.write(f"{len(trips)}\n")
        for start, end, pickup, dropoff in trips:
            f.write(f"{start},{end},{pickup},{dropoff}\n")

    print(f"Saved {len(trips)} trips to {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic taxi trip datasets')
    parser.add_argument('--trips', type=int, default=1000, help='Number of trips to generate')
    parser.add_argument('--locations', type=int, default=10, help='Number of locations')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default=None, help='Output file path')
    args = parser.parse_args()

    # Generate trips
    trips = generate_trips(args.trips, args.locations, args.seed)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        if args.trips <= 50:
            folder = "data/small"
        elif args.trips <= 500:
            folder = "data/medium"
        else:
            folder = "data/large"
        output_path = f"{folder}/synthetic_{args.trips}.txt"

    # Save
    save_trips(trips, output_path)

    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"  Total trips: {len(trips)}")
    print(f"  Locations: {args.locations}")

    start_times = [t[0] for t in trips]
    print(f"  First trip: {min(start_times)//100:02d}:{min(start_times)%100:02d}")
    print(f"  Last trip: {max(start_times)//100:02d}:{max(start_times)%100:02d}")


if __name__ == "__main__":
    main()
