from src.transformation.load_relational_data import load_all_data


def run_pipeline():
    print("🚀 Starting Intelligent Device Health Pipeline...")

    # Step 1: Load full relational data
    db = load_all_data()

    print("✅ Data loaded successfully")

    # You can now access:
    # db["organizations"]
    # db["assets"]
    # db["devices"]
    # db["interfaces"]
    # db["events"]

    print("Pipeline execution completed.")