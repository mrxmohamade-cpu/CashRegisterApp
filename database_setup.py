import os
import bcrypt
import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Float, DateTime, 
                        ForeignKey, Enum, inspect, text, Boolean)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

# --- إعدادات أساسية ---
DB_FILENAME = "cash_register.db"
DATABASE_URL = f"sqlite:///{DB_FILENAME}"
CURRENT_DB_VERSION = 4 # الإصدار الحالي لقاعدة البيانات

# --- إعداد SQLAlchemy ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- نماذج قاعدة البيانات ---
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum('admin', 'user', name='user_roles'), nullable=False, default='user')
    # -- تعديل --: إضافة الحذف المتتالي للجلسات عند حذف المستخدم
    sessions = relationship("CashSession", back_populates="user", cascade="all, delete-orphan")
    flexi_transactions = relationship("FlexiTransaction", back_populates="user")

    def set_password(self, password):
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

class CashSession(Base):
    __tablename__ = 'cash_sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    start_time = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    end_time = Column(DateTime, nullable=True)
    start_balance = Column(Float, nullable=False)
    end_balance = Column(Float, nullable=True)
    status = Column(Enum('open', 'closed', name='session_statuses'), default='open')
    notes = Column(String, nullable=True) # حقل الملاحظات الجديد
    
    # NEW: Flexi tracking
    start_flexi = Column(Float, default=0.0)
    end_flexi = Column(Float, nullable=True)
    
    user = relationship("User", back_populates="sessions")
    transactions = relationship("Transaction", back_populates="session", cascade="all, delete-orphan")
    flexi_transactions = relationship("FlexiTransaction", back_populates="session", cascade="all, delete-orphan")

    @hybrid_property
    def total_expense(self):
        return sum(t.amount for t in self.transactions if t.type == 'expense')
    
    # -- تعديل --: حساب مجموع الفليكسي المدفوع نقدًا فقط
    @hybrid_property
    def total_flexi_paid(self):
        return sum(t.amount for t in self.flexi_transactions if t.is_paid)

    @hybrid_property
    def total_flexi_additions(self):
        return sum(t.amount for t in self.flexi_transactions)
        
    @hybrid_property
    def gross_income(self):
        if self.end_balance is None:
            return 0.0
        return self.end_balance - self.start_balance
        
    @hybrid_property
    def net_cash_difference(self):
        if self.end_balance is None:
            return 0.0
        theoretical_cash_balance = (self.start_balance - self.total_expense)
        # -- تعديل --: الربح الصافي النقدي يخصم منه الفليكسي المدفوع نقدًا
        return self.end_balance - (theoretical_cash_balance + self.total_flexi_paid)
        
    @hybrid_property
    def flexi_consumed(self):
        if self.end_flexi is None:
            return 0.0
        theoretical_flexi_balance = (self.start_flexi or 0.0) + (self.total_flexi_additions or 0.0)
        return theoretical_flexi_balance - self.end_flexi

    @hybrid_property
    def net_profit(self):
        return self.gross_income - self.total_expense

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('cash_sessions.id'))
    type = Column(Enum('income', 'expense', name='transaction_types'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    session = relationship("CashSession", back_populates="transactions")

class FlexiTransaction(Base):
    __tablename__ = 'flexi_transactions'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('cash_sessions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    # -- إضافة --: عمود جديد لتتبع حالة الدفع
    is_paid = Column(Boolean, default=False)
    
    session = relationship("CashSession", back_populates="flexi_transactions")
    user = relationship("User", back_populates="flexi_transactions")

# --- دوال إدارة قاعدة البيانات ---
def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create and populate db_version table
    try:
        db.execute(text("CREATE TABLE IF NOT EXISTS db_version (version INTEGER PRIMARY KEY NOT NULL)"))
        db.execute(text(f"INSERT OR REPLACE INTO db_version (version) VALUES ({CURRENT_DB_VERSION})"))
        db.commit()
    except Exception as e:
        print(f"Failed to create/update db_version table: {e}")
        db.rollback()
        
    # إضافة مستخدم افتراضي (admin)
    admin_exists = db.query(User).filter_by(username='admin').first()
    if not admin_exists:
        admin_user = User(username='admin', role='admin')
        admin_user.set_password('admin')
        db.add(admin_user)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
    db.close()
    
def get_db_version(engine):
    """
    يفحص إصدار قاعدة البيانات بذكاء.
    """
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return 0 # If main tables don't exist, it's a new DB

    if not inspector.has_table("db_version"):
        return 1
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version FROM db_version LIMIT 1"))
            version = result.scalar_one_or_none()
            return version if version is not None else 1
    except Exception:
        return 1

def run_migrations(engine):
    """
    ينفذ جميع الترحيلات المطلوبة حتى تصل قاعدة البيانات إلى أحدث إصدار.
    - يعيد (bool, str) للإشارة إلى النجاح أو الفشل مع رسالة.
    """
    inspector = inspect(engine)
    current_version = get_db_version(engine)
    
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            
            # Migration from v1 to v2 (adds 'notes' column)
            if current_version < 2:
                print("Running migration to version 2...")
                if inspector.has_table('cash_sessions'):
                    columns = [c['name'] for c in inspector.get_columns('cash_sessions')]
                    if 'notes' not in columns:
                        connection.execute(text("ALTER TABLE cash_sessions ADD COLUMN notes VARCHAR(255)"))
                connection.execute(text("CREATE TABLE IF NOT EXISTS db_version (version INTEGER PRIMARY KEY NOT NULL)"))
                connection.execute(text("INSERT OR REPLACE INTO db_version (version) VALUES (2)"))
                current_version = 2
                print("Migration to v2 successful.")

            # Migration from v2 to v3 (adds flexi columns and table)
            if current_version < 3:
                print("Running migration to version 3...")
                if inspector.has_table('cash_sessions'):
                    columns = [c['name'] for c in inspector.get_columns('cash_sessions')]
                    if 'start_flexi' not in columns:
                        connection.execute(text("ALTER TABLE cash_sessions ADD COLUMN start_flexi FLOAT DEFAULT 0.0"))
                    if 'end_flexi' not in columns:
                        connection.execute(text("ALTER TABLE cash_sessions ADD COLUMN end_flexi FLOAT NULL"))
                
                if not inspector.has_table('flexi_transactions'):
                    connection.execute(text("""
                        CREATE TABLE flexi_transactions (
                            id INTEGER NOT NULL, 
                            session_id INTEGER, 
                            user_id INTEGER,
                            amount FLOAT NOT NULL, 
                            description VARCHAR, 
                            timestamp DATETIME, 
                            PRIMARY KEY (id), 
                            FOREIGN KEY(session_id) REFERENCES cash_sessions (id),
                            FOREIGN KEY(user_id) REFERENCES users (id)
                        )
                    """))
                
                connection.execute(text("INSERT OR REPLACE INTO db_version (version) VALUES (3)"))
                current_version = 3
                print("Migration to v3 successful.")
            
            # -- إضافة --: الترحيل من v3 إلى v4 (يضيف عمود is_paid)
            if current_version < 4:
                print("Running migration to version 4...")
                if inspector.has_table('flexi_transactions'):
                    columns = [c['name'] for c in inspector.get_columns('flexi_transactions')]
                    if 'is_paid' not in columns:
                        connection.execute(text("ALTER TABLE flexi_transactions ADD COLUMN is_paid BOOLEAN DEFAULT 0"))
                connection.execute(text("INSERT OR REPLACE INTO db_version (version) VALUES (4)"))
                current_version = 4
                print("Migration to v4 successful.")
                
            trans.commit()
            message = "تم تحديث قاعدة البيانات بنجاح!"
            print(f"All migrations completed: {message}")
            return True, message
            
    except Exception as e:
        message = f"فشل تحديث قاعدة البيانات: {e}"
        print(f"Migration FAILED: {e}")
        try:
            trans.rollback()
        except Exception:
            pass
        return False, message
