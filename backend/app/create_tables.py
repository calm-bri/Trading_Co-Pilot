<<<<<<< HEAD
# from app.core.database import Base, engine
# from app.models import user, trade, alert  # import all your model files

# print("Creating database tables...")
# Base.metadata.create_all(bind=engine)
# print("✅ Tables created successfully!")
=======
from app.core.database import Base, engine
from app.models import user, trade, alert  # import all your model files

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")
>>>>>>> 22d588f1441daecb5784d63a1f084b0589ead99c
