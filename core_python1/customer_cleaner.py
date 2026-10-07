import re
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


class CustomerCleaner:

    def __init__(self, dataframe):
        """
        Store a copy of the dataframe.
        """
        self.df = dataframe.copy()
        logger.info("CustomerCleaner initialized.")

    ########################################################

    def standardize_column_names(self):
        """
        Convert column names into snake_case.
        Example:
        MonthlyCharges -> monthly_charges
        customerID -> customer_id
        StreamingTV -> streaming_tv
        """
        cleaned = []

        for col in self.df.columns:
            col_name = str(col).strip().replace(" ", "_")
            col_name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", col_name)
            col_name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", col_name)
            cleaned.append(col_name.lower())

        self.df.columns = cleaned

        logger.info("Column names standardized.")
        return self

    ########################################################

    def fix_total_charges(self):
        """
        Replace blank strings with NaN
        Convert to float
        """
        try:

            before = self.df["total_charges"].isna().sum()

            self.df["total_charges"] = (
                self.df["total_charges"]
                .replace(" ", pd.NA)
            )

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            after = self.df["total_charges"].isna().sum()

            logger.info(
                f"TotalCharges converted to numeric. "
                f"NaN before={before}, after={after}"
            )

        except Exception as e:
            logger.error(f"Error fixing TotalCharges: {e}")

        return self

    ########################################################

    def normalize_binary_columns(self):
        """
        Convert Yes/No to 1/0
        """

        binary_columns = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies"
        ]

        mapping = {
            "Yes": 1,
            "No": 0
        }

        for col in binary_columns:

            self.df[col] = self.df[col].map(mapping)

        logger.info("Binary columns normalized.")

        return self

    ########################################################

    def handle_nulls(self):
        """
        Fill TotalCharges missing values using MonthlyCharges
        """

        missing_before = self.df["total_charges"].isna().sum()

        self.df["total_charges"] = self.df["total_charges"].fillna(
            self.df["monthly_charges"]
        )

        missing_after = self.df["total_charges"].isna().sum()

        logger.info(
            f"Filled {missing_before - missing_after} missing TotalCharges values."
        )

        return self

    ########################################################

    def clean(self):
        """
        Execute all cleaning steps.
        """

        logger.info("Cleaning started.")

        return (
            self
            .standardize_column_names()
            .fix_total_charges()
            .normalize_binary_columns()
            .handle_nulls()
        )

    ########################################################

    def get_dataframe(self):
        """
        Return cleaned dataframe.
        """

        return self.df