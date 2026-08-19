"""
Importa uma planilha (requisitos.xlsx, materiais.xlsx, ...) para o Postgres.

Uso:
    python scripts/import_excel.py caminho/requisitos.xlsx requirements
    python scripts/import_excel.py caminho/materiais.xlsx materials

Convenções esperadas:
  - requirements: colunas ambiente|environment, area_min, altura_min|height_min, portas|doors
  - materials:     colunas nome|name, categoria|category (demais colunas viram JSON em `properties`)
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.database import SessionLocal  # noqa: E402
from app.models import Requirement, Material  # noqa: E402

COLUMN_ALIASES = {
    "environment": ["ambiente", "environment"],
    "area_min": ["area_min", "área mínima", "area minima"],
    "height_min": ["altura_min", "pé-direito mínimo", "height_min"],
    "doors": ["portas", "doors"],
    "name": ["nome", "name"],
    "category": ["categoria", "category"],
}


def _resolve_column(df: pd.DataFrame, canonical: str) -> str | None:
    normalized = {c.strip().lower(): c for c in df.columns}
    for alias in COLUMN_ALIASES.get(canonical, [canonical]):
        if alias in normalized:
            return normalized[alias]
    return None


def import_requirements(df: pd.DataFrame) -> int:
    env_col = _resolve_column(df, "environment")
    area_col = _resolve_column(df, "area_min")
    height_col = _resolve_column(df, "height_min")
    doors_col = _resolve_column(df, "doors")
    if not env_col:
        raise ValueError("Coluna de ambiente não encontrada (esperado: 'ambiente' ou 'environment').")

    known_cols = {c for c in [env_col, area_col, height_col, doors_col] if c}
    db = SessionLocal()
    count = 0
    try:
        for _, row in df.iterrows():
            extra = {c: row[c] for c in df.columns if c not in known_cols and pd.notna(row[c])}
            stmt = pg_insert(Requirement).values(
                environment=str(row[env_col]).strip().lower(),
                area_min=row[area_col] if area_col else None,
                height_min=row[height_col] if height_col else None,
                doors=int(row[doors_col]) if doors_col and pd.notna(row[doors_col]) else None,
                extra=extra,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["environment"],
                set_={
                    "area_min": stmt.excluded.area_min,
                    "height_min": stmt.excluded.height_min,
                    "doors": stmt.excluded.doors,
                    "extra": stmt.excluded.extra,
                },
            )
            db.execute(stmt)
            count += 1
        db.commit()
    finally:
        db.close()
    return count


def import_materials(df: pd.DataFrame) -> int:
    name_col = _resolve_column(df, "name")
    category_col = _resolve_column(df, "category")
    if not name_col:
        raise ValueError("Coluna de nome não encontrada (esperado: 'nome' ou 'name').")

    known_cols = {c for c in [name_col, category_col] if c}
    db = SessionLocal()
    count = 0
    try:
        for _, row in df.iterrows():
            properties = {c: row[c] for c in df.columns if c not in known_cols and pd.notna(row[c])}
            stmt = pg_insert(Material).values(
                name=str(row[name_col]).strip(),
                category=str(row[category_col]).strip() if category_col and pd.notna(row[category_col]) else None,
                properties=properties,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["name"],
                set_={"category": stmt.excluded.category, "properties": stmt.excluded.properties},
            )
            db.execute(stmt)
            count += 1
        db.commit()
    finally:
        db.close()
    return count


IMPORTERS = {"requirements": import_requirements, "materials": import_materials}


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in IMPORTERS:
        print(f"Uso: python import_excel.py <arquivo.xlsx> <{'|'.join(IMPORTERS)}>")
        sys.exit(1)

    path, table = sys.argv[1], sys.argv[2]
    df = pd.read_excel(path)
    count = IMPORTERS[table](df)
    print(f"OK: {count} linhas importadas em '{table}' a partir de {path}")


if __name__ == "__main__":
    main()
