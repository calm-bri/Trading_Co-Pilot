from app.core.database import Base, engine
from app.models import user, trade, alert  # import all your model files

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")
