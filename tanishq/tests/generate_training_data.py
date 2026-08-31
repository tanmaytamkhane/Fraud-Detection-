import numpy as np
import pandas as pd


def generate_dataset(
    n_legitimate=5000,
    n_ato=1000,
    random_state=42
):
    rng = np.random.default_rng(random_state)

    legitimate = pd.DataFrame({
        "new_device": rng.binomial(1, 0.03, n_legitimate),
        "new_beneficiary": rng.binomial(1, 0.05, n_legitimate),
        "amount_deviation": np.clip(
            rng.normal(0.7, 0.5, n_legitimate),
            0,
            None
        ),
        "velocity_deviation": np.clip(
            rng.normal(0.6, 0.4, n_legitimate),
            0,
            None
        ),
        "location_change": rng.binomial(1, 0.04, n_legitimate),
        "time_deviation": np.clip(
            rng.normal(0.6, 0.5, n_legitimate),
            0,
            None
        ),
        "label": 0
    })

    ato = pd.DataFrame({
        "new_device": rng.binomial(1, 0.75, n_ato),
        "new_beneficiary": rng.binomial(1, 0.80, n_ato),
        "amount_deviation": np.clip(
            rng.normal(3.2, 1.2, n_ato),
            0,
            None
        ),
        "velocity_deviation": np.clip(
            rng.normal(2.5, 1.0, n_ato),
            0,
            None
        ),
        "location_change": rng.binomial(1, 0.65, n_ato),
        "time_deviation": np.clip(
            rng.normal(2.8, 1.1, n_ato),
            0,
            None
        ),
        "label": 1
    })

    dataset = pd.concat(
        [legitimate, ato],
        ignore_index=True
    )

    dataset = dataset.sample(
        frac=1,
        random_state=random_state
    ).reset_index(drop=True)

    return dataset


if __name__ == "__main__":

    data = generate_dataset()

    print("\nDataset shape:")
    print(data.shape)

    print("\nClass distribution:")
    print(data["label"].value_counts())

    print("\nFirst 5 rows:")
    print(data.head())

    data.to_csv(
        "data/ato_training_data.csv",
        index=False
    )

    print("\nSaved to:")
    print("data/ato_training_data.csv")