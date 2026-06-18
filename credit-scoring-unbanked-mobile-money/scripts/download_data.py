from project_package.data import download_uci_default_dataset

if __name__ == "__main__":
    path = download_uci_default_dataset(force=False)
    print(f"Downloaded or found raw UCI dataset at: {path}")
