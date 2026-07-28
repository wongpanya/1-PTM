import sqlite3
from pathlib import Path


DB_PATH = Path(r"C:\Users\Wongpanya.Nu\Documents\1-PTM\phase1_outputs\odos_policy_analytics_prototype.sqlite")


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table' order by name")]
    print("tables:", ", ".join(tables))
    for table in tables:
        count = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
        print(f"{table}: {count}")
    print("completion:", cur.execute("select count(*) from education where project_condition_status='สำเร็จการศึกษา'").fetchone()[0])
    print("income_available:", cur.execute("select count(*) from employment where income_monthly_est is not null").fetchone()[0])
    print("gpa_available:", cur.execute("select count(*) from education where gpa_numeric is not null").fetchone()[0])
    print("sample_students:", cur.execute("select odos_uid, cohort, province, district from students order by odos_uid limit 3").fetchall())
    con.close()


if __name__ == "__main__":
    main()
