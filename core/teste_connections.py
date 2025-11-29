from sqlalchemy import text
from database import engine_a, engine_b

def tester_connexion(engine, nom):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Connexion à {nom} réussie.")
    except Exception as e:
        print(f"❌ Erreur de connexion à {nom} : {e}")

if __name__ == "__main__":
    tester_connexion(engine_a, "replica_a")
    tester_connexion(engine_b, "replica_b")
