from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    user_input = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="init")
    current_state = Column(String)
    dag_definition = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan")
    files = relationship("TaskFile", back_populates="task", cascade="all, delete-orphan")


class TaskStep(Base):
    __tablename__ = "task_steps"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    step_name = Column(String, nullable=False)
    department = Column(String)  # 哪个部门执行
    status = Column(String, nullable=False, default="pending")  # pending|running|success|failed
    input_data = Column(Text)  # JSON string
    output_data = Column(Text)  # JSON string
    error = Column(Text)
    dependencies = Column(Text)  # JSON array string: ["step_id_1", "step_id_2"]
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="steps")


class TaskFile(Base):
    __tablename__ = "task_files"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="files")
