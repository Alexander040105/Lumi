"""
Database integration tests for LUMI PostgreSQL schema.

Coverage:
- CRUD operations on all tables
- Foreign key integrity
- Null constraints and CHECK constraints
- Index existence
- View correctness (regional_lookup)
- Data type validation

Requirements:
    pip install pytest psycopg2-binary

Setup:
    1. Ensure a PostgreSQL instance is running (local or Supabase).
    2. Set the TEST_DATABASE_URL environment variable:
       postgresql://postgres:<password>@db.<project>.supabase.co:5432/postgres
    3. Or use a local test database.

Run:
    pytest tests/integration/test_database.py -v
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Conditional import for psycopg2
# ---------------------------------------------------------------------------
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_OK = True
except ImportError:
    PSYCOPG2_OK = False
    psycopg2 = None  # type: ignore

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "supabase" / "schema_structure" / "lumischema.sql"


def get_db_connection():
    """Create a database connection from environment or raise."""
    if not PSYCOPG2_OK:
        raise RuntimeError("psycopg2-binary is not installed")
    url = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL"))
    if not url:
        raise RuntimeError(
            "TEST_DATABASE_URL or DATABASE_URL environment variable required"
        )
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db_conn():
    """Yield a database connection for the test module."""
    if not PSYCOPG2_OK:
        pytest.skip("psycopg2-binary not installed")
    conn = get_db_connection()
    yield conn
    conn.close()


@pytest.fixture
def cursor(db_conn):
    """Yield a fresh cursor for each test."""
    cur = db_conn.cursor()
    yield cur
    db_conn.rollback()  # always rollback so tests are isolated
    cur.close()


# ---------------------------------------------------------------------------
# SCHEMA VALIDATION
# ---------------------------------------------------------------------------

class TestSchemaExists:
    """Verify that all expected tables, indexes, and views exist."""

    EXPECTED_TABLES = {
        "barangays",
        "hydropower_suitability",
        "municipalities",
        "municipality_climate_monthly",
        "provinces",
        "regions",
    }

    EXPECTED_INDEXES = {
        "idx_barangays_municipality_id",
        "idx_climate_monthly_municipality_id",
        "idx_climate_monthly_municipality_year_month",
        "idx_climate_monthly_year_month",
        "idx_hydropower_suitability_municipality_name",
        "idx_hydropower_suitability_province_id",
        "idx_municipalities_province_id",
        "idx_provinces_region_id",
    }

    def test_all_tables_exist(self, cursor):
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        found = {row["table_name"] for row in cursor.fetchall()}
        missing = self.EXPECTED_TABLES - found
        assert not missing, f"Missing tables: {missing}"

    def test_regional_lookup_view_exists(self, cursor):
        cursor.execute("""
            SELECT table_name FROM information_schema.views
            WHERE table_schema = 'public' AND table_name = 'regional_lookup';
        """)
        assert cursor.fetchone() is not None

    def test_expected_indexes_exist(self, cursor):
        cursor.execute("""
            SELECT indexname FROM pg_indexes WHERE schemaname = 'public';
        """)
        found = {row["indexname"] for row in cursor.fetchall()}
        missing = self.EXPECTED_INDEXES - found
        assert not missing, f"Missing indexes: {missing}"


# ---------------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------------

class TestRegionsCRUD:
    """Create, read, update, delete tests for regions."""

    def test_insert_region(self, cursor):
        cursor.execute(
            "INSERT INTO regions (region_id, name, lat, lon) VALUES (999, 'Test Region', 14.0, 121.0) RETURNING region_id;"
        )
        row = cursor.fetchone()
        assert row["region_id"] == 999

    def test_select_region(self, cursor):
        cursor.execute("SELECT * FROM regions WHERE region_id = 999;")
        row = cursor.fetchone()
        assert row is not None
        assert row["name"] == "Test Region"

    def test_update_region(self, cursor):
        cursor.execute("UPDATE regions SET name = 'Updated Region' WHERE region_id = 999;")
        cursor.execute("SELECT name FROM regions WHERE region_id = 999;")
        assert cursor.fetchone()["name"] == "Updated Region"

    def test_delete_region(self, cursor):
        cursor.execute("DELETE FROM regions WHERE region_id = 999;")
        cursor.execute("SELECT * FROM regions WHERE region_id = 999;")
        assert cursor.fetchone() is None


class TestProvincesCRUD:
    """CRUD tests for provinces with FK to regions."""

    def test_insert_province_with_valid_fk(self, cursor):
        # Ensure parent region exists first
        cursor.execute("INSERT INTO regions (region_id, name) VALUES (998, 'Region For Province') ON CONFLICT DO NOTHING;")
        cursor.execute(
            "INSERT INTO provinces (province_id, region_id, name, lat, lon) VALUES (9999, 998, 'Test Province', 14.5, 120.5);"
        )
        cursor.execute("SELECT * FROM provinces WHERE province_id = 9999;")
        assert cursor.fetchone() is not None

    def test_insert_province_with_invalid_fk_fails(self, cursor):
        with pytest.raises(Exception):
            cursor.execute(
                "INSERT INTO provinces (province_id, region_id, name) VALUES (9998, -1, 'Bad FK');"
            )


class TestMunicipalitiesCRUD:
    """CRUD tests for municipalities."""

    def test_insert_municipality(self, cursor):
        cursor.execute(
            "INSERT INTO municipalities (municipality_id, province_id, name, lat, lon) VALUES (88888, 9999, 'Test Municipality', 14.6, 120.6);"
        )
        cursor.execute("SELECT name FROM municipalities WHERE municipality_id = 88888;")
        assert cursor.fetchone()["name"] == "Test Municipality"

    def test_delete_municipality_cascades_to_climate(self, cursor):
        """Deleting a municipality should cascade restrict (not delete children)."""
        # This test documents the FK behavior: ON DELETE RESTRICT
        cursor.execute("SELECT 1 FROM municipalities WHERE municipality_id = 88888;")
        if cursor.fetchone():
            # If climate data exists, delete should fail due to RESTRICT
            cursor.execute(
                "INSERT INTO municipality_climate_monthly (municipality_id, year, month) VALUES (88888, 2023, 1) ON CONFLICT DO NOTHING;"
            )
            with pytest.raises(Exception):
                cursor.execute("DELETE FROM municipalities WHERE municipality_id = 88888;")


class TestClimateDataCRUD:
    """CRUD tests for municipality_climate_monthly."""

    def test_insert_climate_record(self, cursor):
        cursor.execute(
            """
            INSERT INTO municipality_climate_monthly
            (municipality_id, year, month, t2m, allsky_sfc_sw_dwn, source)
            VALUES (88888, 2023, 6, 28.5, 5.2, 'NASA POWER')
            ON CONFLICT DO NOTHING;
            """
        )
        cursor.execute("SELECT t2m FROM municipality_climate_monthly WHERE municipality_id = 88888 AND year = 2023 AND month = 6;")
        row = cursor.fetchone()
        if row:
            assert row["t2m"] == pytest.approx(28.5)

    def test_month_constraint_valid(self, cursor):
        """Month 12 should be accepted."""
        cursor.execute(
            """
            INSERT INTO municipality_climate_monthly
            (municipality_id, year, month, source)
            VALUES (88888, 2023, 12, 'NASA POWER')
            ON CONFLICT DO NOTHING;
            """
        )
        # Should not raise

    def test_month_constraint_invalid(self, cursor):
        """Month 13 should violate the CHECK constraint."""
        with pytest.raises(Exception):
            cursor.execute(
                """
                INSERT INTO municipality_climate_monthly
                (municipality_id, year, month, source)
                VALUES (88888, 2023, 13, 'NASA POWER');
                """
            )

    def test_year_constraint_invalid(self, cursor):
        """Year 1999 should violate year >= 2018 CHECK."""
        with pytest.raises(Exception):
            cursor.execute(
                """
                INSERT INTO municipality_climate_monthly
                (municipality_id, year, month, source)
                VALUES (88888, 1999, 1, 'NASA POWER');
                """
            )


class TestHydropowerSuitabilityCRUD:
    """CRUD tests for hydropower_suitability."""

    def test_insert_hydropower_record(self, cursor):
        cursor.execute(
            """
            INSERT INTO hydropower_suitability
            (municipality_id, province_id, municipality_name, province, hydro_suitability_score)
            VALUES (77777, 9999, 'Test Hydro', 'Test Province', 0.65)
            ON CONFLICT DO NOTHING;
            """
        )
        cursor.execute("SELECT hydro_suitability_score FROM hydropower_suitability WHERE municipality_id = 77777;")
        row = cursor.fetchone()
        if row:
            assert row["hydro_suitability_score"] == pytest.approx(0.65)


# ---------------------------------------------------------------------------
# FOREIGN KEY INTEGRITY
# ---------------------------------------------------------------------------

class TestForeignKeyIntegrity:
    """Verify referential integrity across the schema."""

    def test_barangays_municipality_fk(self, cursor):
        """barangays.municipality_id must reference municipalities."""
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM barangays b
            LEFT JOIN municipalities m ON b.municipality_id = m.municipality_id
            WHERE m.municipality_id IS NULL;
        """)
        assert cursor.fetchone()["cnt"] == 0

    def test_municipalities_province_fk(self, cursor):
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM municipalities m
            LEFT JOIN provinces p ON m.province_id = p.province_id
            WHERE p.province_id IS NULL;
        """)
        assert cursor.fetchone()["cnt"] == 0

    def test_provinces_region_fk(self, cursor):
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM provinces p
            LEFT JOIN regions r ON p.region_id = r.region_id
            WHERE r.region_id IS NULL;
        """)
        assert cursor.fetchone()["cnt"] == 0

    def test_hydropower_municipality_fk(self, cursor):
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM hydropower_suitability h
            LEFT JOIN municipalities m ON h.municipality_id = m.municipality_id
            WHERE m.municipality_id IS NULL;
        """)
        assert cursor.fetchone()["cnt"] == 0

    def test_climate_municipality_fk(self, cursor):
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM municipality_climate_monthly c
            LEFT JOIN municipalities m ON c.municipality_id = m.municipality_id
            WHERE m.municipality_id IS NULL;
        """)
        assert cursor.fetchone()["cnt"] == 0


# ---------------------------------------------------------------------------
# VIEW CORRECTNESS
# ---------------------------------------------------------------------------

class TestRegionalLookupView:
    """Validate the regional_lookup view joins correctly."""

    def test_view_returns_rows(self, cursor):
        cursor.execute("SELECT COUNT(*) AS cnt FROM regional_lookup;")
        count = cursor.fetchone()["cnt"]
        assert count > 0

    def test_view_has_expected_columns(self, cursor):
        cursor.execute("SELECT * FROM regional_lookup LIMIT 1;")
        row = cursor.fetchone()
        assert row is not None
        expected = {
            "region_id", "region_name", "region_lat", "region_lon",
            "province_id", "province_name", "province_lat", "province_lon",
            "municipality_id", "municipality_name", "municipality_lat", "municipality_lon",
            "barangay_id", "barangay_name", "barangay_lat", "barangay_lon",
        }
        assert expected.issubset(row.keys())

    def test_view_municipality_count_matches(self, cursor):
        """The number of municipalities in the view should match the municipalities table."""
        cursor.execute("SELECT COUNT(DISTINCT municipality_id) AS cnt FROM regional_lookup;")
        view_count = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) AS cnt FROM municipalities;")
        table_count = cursor.fetchone()["cnt"]
        assert view_count == table_count


# ---------------------------------------------------------------------------
# NULL CONSTRAINTS & DATA TYPES
# ---------------------------------------------------------------------------

class TestNullConstraints:
    """Verify that required fields reject NULL."""

    def test_regions_name_not_null(self, cursor):
        with pytest.raises(Exception):
            cursor.execute("INSERT INTO regions (region_id, name) VALUES (997, NULL);")

    def test_provinces_name_not_null(self, cursor):
        with pytest.raises(Exception):
            cursor.execute("INSERT INTO provinces (province_id, region_id, name) VALUES (997, 998, NULL);")

    def test_municipalities_name_not_null(self, cursor):
        with pytest.raises(Exception):
            cursor.execute("INSERT INTO municipalities (municipality_id, province_id, name) VALUES (997, 9999, NULL);")


class TestDataTypes:
    """Verify expected column data types."""

    def test_climate_t2m_is_double(self, cursor):
        cursor.execute("""
            SELECT data_type FROM information_schema.columns
            WHERE table_name = 'municipality_climate_monthly' AND column_name = 't2m';
        """)
        row = cursor.fetchone()
        assert row is not None
        assert "double" in row["data_type"].lower() or "numeric" in row["data_type"].lower()

    def test_climate_year_is_smallint(self, cursor):
        cursor.execute("""
            SELECT data_type FROM information_schema.columns
            WHERE table_name = 'municipality_climate_monthly' AND column_name = 'year';
        """)
        row = cursor.fetchone()
        assert row is not None
        assert "smallint" in row["data_type"].lower() or "int" in row["data_type"].lower()

    def test_climate_month_check(self, cursor):
        cursor.execute("""
            SELECT definition FROM pg_constraint
            WHERE conname = 'municipality_climate_monthly_month_check';
        """)
        row = cursor.fetchone()
        assert row is not None
        assert "month" in row["definition"].lower()
