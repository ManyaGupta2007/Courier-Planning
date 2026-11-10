"""Create the medium and large sample datasets (reproducible, seeded)."""

from courier.dataset import generate_dataset, save_dataset

if __name__ == "__main__":
    save_dataset(generate_dataset("medium", 30, 60, 80, seed=1), "data/medium.json")
    save_dataset(generate_dataset("large", 150, 1000, 200, seed=2), "data/large.json")
    print("Wrote data/medium.json and data/large.json")
