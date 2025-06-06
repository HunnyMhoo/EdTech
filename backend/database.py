from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

class DatabaseManager:
    """
    Manages the connection to the MongoDB database.
    """
    client: AsyncIOMotorClient = None

    def connect_to_database(self):
        """
        Connects to the MongoDB database using the URI from the global settings.
        """
        print("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(settings.DATABASE_URL)
        print("Successfully connected to MongoDB.")

    def close_database_connection(self):
        """
        Closes the connection to the MongoDB database.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

    def get_database(self):
        """
        Returns the database instance.
        """
        if not self.client:
            raise Exception("Database not connected. Call connect_to_database first.")
        
        return self.client[settings.MONGO_DB_NAME]

# Create a singleton instance of the DatabaseManager
db_manager = DatabaseManager() 