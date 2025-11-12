"""CSV file management with atomic writes and file locking."""

import csv
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import sys
from contextlib import contextmanager

# Import fcntl only on Unix systems (not available on Windows)
if sys.platform != "win32":
    import fcntl
else:
    fcntl = None

from config import config


class CSVManager:
    """Manages CSV file operations with atomic writes and locking."""

    def __init__(self):
        """Initialize CSV manager."""
        config.ensure_data_dir()

    @contextmanager
    def _file_lock(self, filepath: Path, mode: str = "r"):
        """Context manager for file locking (Unix only, no-op on Windows)."""
        # Ensure file exists for reading
        if "r" in mode and not filepath.exists():
            filepath.touch()

        with open(filepath, mode, encoding="utf-8", newline="") as f:
            try:
                # Only use file locking on Unix systems
                if fcntl is not None:
                    lock_mode = fcntl.LOCK_SH if "r" in mode else fcntl.LOCK_EX
                    fcntl.flock(f.fileno(), lock_mode)
                yield f
            finally:
                if fcntl is not None:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def read_csv(self, filename: str) -> List[Dict[str, Any]]:
        """
        Read CSV file and return list of dictionaries.

        Args:
            filename: Name of the CSV file (e.g., 'transactions.csv')

        Returns:
            List of dictionaries representing rows
        """
        filepath = config.get_data_path(filename)

        # Return empty list if file doesn't exist
        if not filepath.exists():
            return []

        with self._file_lock(filepath, "r") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def write_csv(
        self, filename: str, data: List[Dict[str, Any]], fieldnames: List[str]
    ) -> None:
        """
        Write data to CSV file atomically.

        Args:
            filename: Name of the CSV file
            data: List of dictionaries to write
            fieldnames: List of field names for CSV header
        """
        filepath = config.get_data_path(filename)

        # Create temporary file in the same directory
        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent, prefix=f".{filename}.", suffix=".tmp"
        )

        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8", newline="") as temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            # Atomic rename
            shutil.move(temp_path, filepath)
        except Exception as e:
            # Clean up temp file on error
            Path(temp_path).unlink(missing_ok=True)
            raise e

    def append_csv(
        self, filename: str, row: Dict[str, Any], fieldnames: List[str]
    ) -> None:
        """
        Append a single row to CSV file.

        Args:
            filename: Name of the CSV file
            row: Dictionary representing the row to append
            fieldnames: List of field names
        """
        filepath = config.get_data_path(filename)

        # If file doesn't exist, write with header
        if not filepath.exists():
            self.write_csv(filename, [row], fieldnames)
            return

        with self._file_lock(filepath, "a") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(row)

    def read_json(self, filename: str) -> Dict[str, Any]:
        """
        Read JSON file.

        Args:
            filename: Name of the JSON file (e.g., 'settings.json')

        Returns:
            Dictionary representing JSON content
        """
        filepath = config.get_data_path(filename)

        if not filepath.exists():
            return {}

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_json(self, filename: str, data: Dict[str, Any]) -> None:
        """
        Write data to JSON file atomically.

        Args:
            filename: Name of the JSON file
            data: Dictionary to write
        """
        filepath = config.get_data_path(filename)

        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent, prefix=f".{filename}.", suffix=".tmp"
        )

        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as temp_file:
                json.dump(data, temp_file, indent=2, ensure_ascii=False)

            # Atomic rename
            shutil.move(temp_path, filepath)
        except Exception as e:
            Path(temp_path).unlink(missing_ok=True)
            raise e

    def update_csv_row(
        self,
        filename: str,
        row_id: str,
        updated_row: Dict[str, Any],
        fieldnames: List[str],
        id_field: str = "id",
    ) -> bool:
        """
        Update a single row in CSV file by ID.

        Args:
            filename: Name of the CSV file
            row_id: ID of the row to update
            updated_row: Dictionary with updated values
            fieldnames: List of field names
            id_field: Name of the ID field (default: 'id')

        Returns:
            True if row was found and updated, False otherwise
        """
        data = self.read_csv(filename)
        found = False

        for i, row in enumerate(data):
            if row.get(id_field) == row_id:
                data[i] = updated_row
                found = True
                break

        if found:
            self.write_csv(filename, data, fieldnames)

        return found

    def delete_csv_row(
        self, filename: str, row_id: str, fieldnames: List[str], id_field: str = "id"
    ) -> bool:
        """
        Delete a single row from CSV file by ID.

        Args:
            filename: Name of the CSV file
            row_id: ID of the row to delete
            fieldnames: List of field names
            id_field: Name of the ID field (default: 'id')

        Returns:
            True if row was found and deleted, False otherwise
        """
        data = self.read_csv(filename)
        original_length = len(data)

        data = [row for row in data if row.get(id_field) != row_id]

        if len(data) < original_length:
            self.write_csv(filename, data, fieldnames)
            return True

        return False

    def read_by_id(
        self, filename: str, row_id: str, id_field: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """
        Read a single row by ID.

        Args:
            filename: Name of the CSV file
            row_id: ID of the row to read
            id_field: Name of the ID field (default: 'id')

        Returns:
            Row dictionary if found, None otherwise
        """
        data = self.read_csv(filename)
        for row in data:
            if row.get(id_field) == row_id:
                return row
        return None

    def append(self, filename: str, row: Dict[str, Any]) -> None:
        """
        Append a row to CSV file (auto-detects fieldnames from file).

        Args:
            filename: Name of the CSV file
            row: Row data to append
        """
        filepath = config.DATA_DIR / filename

        # Read existing data to get fieldnames
        if filepath.exists():
            with self._file_lock(filepath, "r") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
        else:
            # If file doesn't exist, use row keys as fieldnames
            fieldnames = list(row.keys())
            # Create file with header
            with self._file_lock(filepath, "w") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

        # Append the row
        self.append_csv(filename, row, fieldnames)

    def update(
        self,
        filename: str,
        row_id: str,
        updated_row: Dict[str, Any],
        id_field: str = "id",
    ) -> bool:
        """
        Update a row by ID (auto-detects fieldnames from file).

        Args:
            filename: Name of the CSV file
            row_id: ID of the row to update
            updated_row: Updated row data
            id_field: Name of the ID field (default: 'id')

        Returns:
            True if row was found and updated, False otherwise
        """
        filepath = config.DATA_DIR / filename

        # Read existing data to get fieldnames
        with self._file_lock(filepath, "r") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        return self.update_csv_row(filename, row_id, updated_row, fieldnames, id_field)

    def delete(self, filename: str, row_id: str, id_field: str = "id") -> bool:
        """
        Delete a row by ID (auto-detects fieldnames from file).

        Args:
            filename: Name of the CSV file
            row_id: ID of the row to delete
            id_field: Name of the ID field (default: 'id')

        Returns:
            True if row was found and deleted, False otherwise
        """
        filepath = config.DATA_DIR / filename

        # Read existing data to get fieldnames
        with self._file_lock(filepath, "r") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        return self.delete_csv_row(filename, row_id, fieldnames, id_field)


# Singleton instance
csv_manager = CSVManager()
